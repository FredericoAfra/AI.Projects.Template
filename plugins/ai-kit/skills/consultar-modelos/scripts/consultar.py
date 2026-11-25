#!/usr/bin/env python3
"""Consulta agentes de outros modelos pelos CLIs deles, em modo somente leitura.

  python consultar.py --listar
  python consultar.py --para codex,gemini --pergunta "Revise o plano em plano/PLANO.md"
  python consultar.py --para todos --pergunta-arquivo pergunta.md --diff --arquivos src/a.py
  python consultar.py --para gemini --modelo gemini=<nome-do-modelo> --pergunta "..."

A pergunta completa e gravada em .ai-kit/consultas/<data>/pergunta.md e cada CLI
recebe so uma instrucao curta apontando para esse arquivo (evita limites de
tamanho e problemas de aspas no Windows). As respostas ficam na mesma pasta.
Roda as consultas em paralelo. Usa as assinaturas ja logadas em cada CLI.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

# Cada CLI: executavel, como montar o comando (somente leitura) e flag de modelo.
CLIS = {
    # OpenAI Codex CLI (usa login do ChatGPT ou chave da OpenAI)
    "codex": {"exe": "codex", "cmd": lambda exe, p: [exe, "exec", "--sandbox", "read-only", "--skip-git-repo-check", p],
              "model_flag": "-m", "nome": "OpenAI Codex / ChatGPT"},
    # Google Gemini CLI (sem --yolo: acoes que pedem aprovacao sao negadas no modo headless)
    "gemini": {"exe": "gemini", "cmd": lambda exe, p: [exe, "-p", p], "model_flag": "-m", "nome": "Google Gemini"},
    # GitHub Copilot CLI (sem --allow-all-tools: ferramentas que pedem aprovacao sao negadas)
    "copilot": {"exe": "copilot", "cmd": lambda exe, p: [exe, "-p", p], "model_flag": "--model", "nome": "GitHub Copilot"},
    # Claude Code (para quando outro agente quiser consultar o Claude com este mesmo script)
    "claude": {"exe": "claude", "cmd": lambda exe, p: [exe, "-p", p, "--permission-mode", "plan"],
               "model_flag": "--model", "nome": "Claude Code"},
}

INSTRUCAO = (
    "Leia o arquivo {arq} (caminho relativo a pasta atual) e responda ao que ele pede. "
    "Voce esta sendo consultado por outro agente de IA como revisor independente: "
    "NAO altere nenhum arquivo. Responda em portugues, de forma objetiva, citando arquivo:linha quando aplicavel."
)


def disponiveis() -> dict:
    return {k: shutil.which(v["exe"]) for k, v in CLIS.items()}


def git_diff() -> str:
    try:
        out = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        return out.stdout.strip()
    except FileNotFoundError:
        return ""


def rodar(cli: str, exe: str, instrucao: str, modelo: str | None, timeout: int, pasta: Path) -> tuple[str, int, str]:
    cmd = CLIS[cli]["cmd"](exe, instrucao)
    if modelo:
        cmd += [CLIS[cli]["model_flag"], modelo]
    inicio = dt.datetime.now()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, stdin=subprocess.DEVNULL)
        saida, codigo = r.stdout.strip(), r.returncode
        if codigo != 0 and r.stderr.strip():
            saida += "\n\n[stderr]\n" + r.stderr.strip()[-3000:]
    except subprocess.TimeoutExpired:
        saida, codigo = f"[tempo esgotado apos {timeout}s]", 124
    seg = (dt.datetime.now() - inicio).seconds
    (pasta / f"{cli}.md").write_text(f"# Resposta de {CLIS[cli]['nome']} ({seg}s, codigo {codigo})\n\n{saida}\n", encoding="utf-8")
    return cli, codigo, saida


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listar", action="store_true", help="mostra quais CLIs estao instalados")
    ap.add_argument("--para", default="todos", help="codex,gemini,copilot,claude ou 'todos' (os instalados, menos claude)")
    ap.add_argument("--pergunta", help="texto da pergunta")
    ap.add_argument("--pergunta-arquivo", help="arquivo com a pergunta")
    ap.add_argument("--diff", action="store_true", help="anexa o git diff atual")
    ap.add_argument("--arquivos", nargs="*", default=[], help="arquivos para o outro agente ler (so os caminhos)")
    ap.add_argument("--modelo", action="append", default=[], help="cli=modelo (repetivel), ex.: codex=<modelo>")
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args()

    disp = disponiveis()
    if a.listar:
        for k, v in disp.items():
            print(f"{k:<8} {'OK  ' + v if v else 'nao instalado'}")
        return

    if a.para == "todos":
        alvos = [k for k, v in disp.items() if v and k != "claude"]
    else:
        alvos = [x.strip() for x in a.para.split(",") if x.strip()]
    desconhecidos = [x for x in alvos if x not in CLIS]
    if desconhecidos:
        sys.exit(f"erro: CLI desconhecido {desconhecidos}; opcoes: {list(CLIS)}")
    faltando = [x for x in alvos if not disp.get(x)]
    alvos = [x for x in alvos if disp.get(x)]
    if faltando:
        print(f"aviso: nao instalados: {', '.join(faltando)} (veja a skill consultar-modelos para instalar)")
    if not alvos:
        sys.exit("erro: nenhum CLI disponivel para consultar")

    pergunta = a.pergunta or ""
    if a.pergunta_arquivo:
        pergunta += "\n\n" + Path(a.pergunta_arquivo).read_text(encoding="utf-8")
    if not pergunta.strip():
        sys.exit("erro: informe --pergunta ou --pergunta-arquivo")
    if a.arquivos:
        pergunta += "\n\n## Arquivos para ler\n" + "\n".join(f"- {f}" for f in a.arquivos)
    if a.diff:
        d = git_diff()
        pergunta += "\n\n## Mudancas (git diff)\n```diff\n" + (d or "(sem diff)") + "\n```"

    pasta = Path(".ai-kit") / "consultas" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    pasta.mkdir(parents=True, exist_ok=True)
    gi = Path(".ai-kit") / ".gitignore"
    if not gi.exists():
        gi.write_text("consultas/\n", encoding="utf-8")
    arq = (pasta / "pergunta.md").as_posix()
    Path(arq).write_text(pergunta.strip() + "\n", encoding="utf-8")
    modelos = dict(m.split("=", 1) for m in a.modelo if "=" in m)
    instr = INSTRUCAO.format(arq=arq)

    print(f"Consultando {', '.join(alvos)} (pergunta em {arq}) ...", flush=True)
    falhas = 0
    with cf.ThreadPoolExecutor(max_workers=len(alvos)) as ex:
        futuros = [ex.submit(rodar, c, disp[c], instr, modelos.get(c), a.timeout, pasta) for c in alvos]
        for f in cf.as_completed(futuros):
            cli, codigo, saida = f.result()
            falhas += codigo != 0
            status = "ok" if codigo == 0 else f"FALHOU (codigo {codigo})"
            texto = saida if len(saida) <= 8000 else saida[:8000] + f"\n[... truncado; completo em {pasta.as_posix()}/{cli}.md]"
            print(f"\n===== {CLIS[cli]['nome']} [{cli}] — {status} =====\n{texto}")
    print(f"\nRespostas salvas em {pasta.as_posix()}/")
    if falhas == len(alvos):
        sys.exit(1)


if __name__ == "__main__":
    main()
