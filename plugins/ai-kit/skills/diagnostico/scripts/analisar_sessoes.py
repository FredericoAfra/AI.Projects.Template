#!/usr/bin/env python3
"""Analisa o historico de sessoes do Claude Code e mostra onde melhorar.

  python analisar_sessoes.py                 # projeto da pasta atual, ultimos 30 dias
  python analisar_sessoes.py --dias 7
  python analisar_sessoes.py --projeto C:/caminho/projeto
  python analisar_sessoes.py --todos         # todos os projetos

Le ~/.claude/projects/<projeto>/*.jsonl (somente leitura) e imprime um relatorio
em Markdown: custo e tokens por modelo, ferramentas com erro, skills/agentes
usados e nunca usados, sinais de correcao do usuario e sugestoes.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

CORRECAO = re.compile(
    r"^\s*(n[aã]o[ ,.!]|nao era|errad|est[aá] errado|pare\b|para de|de novo|refa[cz]|desfa[cz]|volta|"
    r"ainda n[aã]o|n[aã]o funcion|n[aã]o foi isso|wrong|stop|undo)", re.I)
KIT = Path(__file__).resolve().parents[3]  # .../plugins/ai-kit


def pasta_projetos() -> Path:
    base = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(base) if base else Path.home() / ".claude") / "projects"


def codificar(p: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(p.resolve())).lower()


def textos_usuario(msg) -> list[str]:
    c = msg.get("content")
    if isinstance(c, str):
        return [c]
    out = []
    for item in c or []:
        if isinstance(item, dict) and item.get("type") == "text":
            out.append(item.get("text", ""))
    return out


def kit_itens() -> tuple[set, set]:
    skills = {p.parent.name for p in (KIT / "skills").glob("*/SKILL.md")}
    agentes = {p.stem for p in (KIT / "agents").glob("*.md")}
    return skills, agentes


def analisar(arquivos: list[Path]) -> dict:
    r = {
        "sessoes": {}, "ferramentas": collections.Counter(), "erros": collections.Counter(),
        "exemplos_erro": collections.defaultdict(list), "skills": collections.Counter(),
        "agentes": collections.Counter(), "agentes_modelo": collections.Counter(),
        "correcoes": [], "interrupcoes": 0, "compactacoes": 0, "modelos": collections.defaultdict(lambda: collections.Counter()),
    }
    nomes_tool: dict[str, str] = {}
    for f in arquivos:
        for linha in f.open(encoding="utf-8", errors="replace"):
            try:
                d = json.loads(linha)
            except json.JSONDecodeError:
                continue
            t, sid = d.get("type"), d.get("sessionId", f.stem)
            s = r["sessoes"].setdefault(sid, {"titulo": "", "prompts": 0, "custo": 0.0, "duracao_min": 0,
                                              "linhas": 0, "inicio": d.get("timestamp", ""), "uso": {}})
            if not s["inicio"] and d.get("timestamp"):
                s["inicio"] = d["timestamp"]
            if t == "custom-title" and d.get("customTitle"):
                s["titulo"] = d["customTitle"]
            elif t == "cost-state":  # fica com o ultimo estado da sessao
                s["custo"] = d.get("totalCostUSD", 0) or 0
                s["duracao_min"] = round((d.get("totalDuration", 0) or 0) / 60000)
                s["linhas"] = (d.get("totalLinesAdded", 0) or 0) + (d.get("totalLinesRemoved", 0) or 0)
                s["uso"] = d.get("modelUsage", {}) or {}
            elif t == "system" and "compact" in str(d.get("subtype", "")):
                r["compactacoes"] += 1
            elif t == "assistant":
                for item in d.get("message", {}).get("content", []) or []:
                    if not isinstance(item, dict) or item.get("type") != "tool_use":
                        continue
                    nome, inp = item.get("name", "?"), item.get("input", {}) or {}
                    nomes_tool[item.get("id", "")] = nome
                    r["ferramentas"][nome] += 1
                    if nome == "Skill":
                        r["skills"][str(inp.get("skill", "?"))] += 1
                    elif nome in ("Agent", "Task"):
                        ag = str(inp.get("subagent_type") or "general-purpose")
                        r["agentes"][ag] += 1
                        r["agentes_modelo"][f"{ag} -> {inp.get('model', 'padrao')}/{inp.get('effort', 'padrao')}"] += 1
            elif t == "user" and not d.get("isSidechain"):
                msg = d.get("message", {}) or {}
                conteudo = msg.get("content")
                if isinstance(conteudo, list):
                    for item in conteudo:
                        if isinstance(item, dict) and item.get("type") == "tool_result" and item.get("is_error"):
                            nome = nomes_tool.get(item.get("tool_use_id", ""), "?")
                            r["erros"][nome] += 1
                            txt = item.get("content")
                            txt = txt if isinstance(txt, str) else json.dumps(txt, ensure_ascii=False)
                            if len(r["exemplos_erro"][nome]) < 3:
                                r["exemplos_erro"][nome].append(re.sub(r"\s+", " ", txt)[:160])
                for txt in textos_usuario(msg):
                    if txt.lstrip().startswith("<") or not txt.strip():
                        continue
                    if "[Request interrupted" in txt:
                        r["interrupcoes"] += 1
                        continue
                    if isinstance(conteudo, str) or d.get("promptId"):
                        s["prompts"] += 1
                    if CORRECAO.search(txt):
                        r["correcoes"].append(re.sub(r"\s+", " ", txt)[:140])
    return r


def relatorio(r: dict, titulo: str) -> str:
    L = [f"# Diagnostico — {titulo}", ""]
    ses = [s for s in r["sessoes"].values() if s["prompts"] or s["custo"]]
    custo = sum(s["custo"] for s in ses)
    L += [f"**Sessoes:** {len(ses)} · **custo estimado:** US$ {custo:.2f} · **pedidos do usuario:** {sum(s['prompts'] for s in ses)} "
          f"· **interrupcoes:** {r['interrupcoes']} · **compactacoes de contexto:** {r['compactacoes']}", ""]

    tok = collections.defaultdict(collections.Counter)
    for s in ses:
        for modelo, u in s["uso"].items():
            for k in ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens"):
                tok[modelo][k] += u.get(k, 0) or 0
            tok[modelo]["custo"] += u.get("costUSD", 0) or 0
    if tok:
        L += ["## Tokens por modelo", "| Modelo | Entrada | Saida | Cache lido | Cache criado |", "|---|---|---|---|---|"]
        for m, c in sorted(tok.items(), key=lambda x: -x[1]["outputTokens"]):
            L.append(f"| {m} | {c['inputTokens']:,} | {c['outputTokens']:,} | {c['cacheReadInputTokens']:,} | {c['cacheCreationInputTokens']:,} |")
        L.append("")

    L += ["## Sessoes mais caras", "| Sessao | Custo | Min | Pedidos | Linhas alteradas |", "|---|---|---|---|---|"]
    for s in sorted(ses, key=lambda x: -x["custo"])[:8]:
        L.append(f"| {(s['titulo'] or s['inicio'][:16])[:50]} | {s['custo']:.2f} | {s['duracao_min']} | {s['prompts']} | {s['linhas']} |")
    L.append("")

    L += ["## Ferramentas", "| Ferramenta | Usos | Erros | % erro |", "|---|---|---|---|"]
    for nome, n in r["ferramentas"].most_common(12):
        e = r["erros"].get(nome, 0)
        L.append(f"| {nome} | {n} | {e} | {100 * e / n:.0f}% |")
    L.append("")
    if r["erros"]:
        L.append("**Exemplos de erro:**")
        for nome, ex in r["exemplos_erro"].items():
            for x in ex:
                L.append(f"- `{nome}`: {x}")
        L.append("")

    skills_kit, agentes_kit = kit_itens()
    usados_s = {k.split(":")[-1] for k in r["skills"]}
    L += ["## Skills e agentes", f"- Skills usadas: {dict(r['skills']) or 'nenhuma'}",
          f"- Agentes usados: {dict(r['agentes']) or 'nenhum'}"]
    if r["agentes_modelo"]:
        L.append(f"- Agente -> modelo/esforco: {dict(r['agentes_modelo'])}")
    nunca_s = sorted(skills_kit - usados_s)
    nunca_a = sorted(agentes_kit - set(r["agentes"]))
    L += [f"- **Skills do kit nunca usadas:** {', '.join(nunca_s) or '-'}",
          f"- **Agentes do kit nunca usados:** {', '.join(nunca_a) or '-'}", ""]

    if r["correcoes"]:
        L += [f"## Possiveis correcoes do usuario ({len(r['correcoes'])})"] + [f"- {c}" for c in r["correcoes"][:15]] + [""]

    sug = []
    total_pedidos = sum(s["prompts"] for s in ses) or 1
    for nome, e in r["erros"].items():
        n = r["ferramentas"].get(nome, 0)
        if e >= 3 and n and e / n >= 0.15:
            sug.append(f"`{nome}` falha em {100 * e / n:.0f}% das chamadas: veja os exemplos e registre o contorno no AGENTS.md.")
    if len(r["correcoes"]) / total_pedidos > 0.1:
        sug.append("Mais de 10% dos pedidos parecem correcoes: transforme as recorrentes em regras (skill `criar`).")
    if r["compactacoes"]:
        sug.append("Houve compactacao de contexto: use plano/plano.json + progresso.md e delegue leituras grandes a subagentes.")
    caro = [m for m in tok if "opus" in m]
    if caro and not r["agentes"]:
        sug.append("Todo o trabalho rodou no modelo principal: use `executar` para delegar tarefas P/M a haiku/sonnet.")
    if nunca_s:
        sug.append(f"Skills nunca usadas ({', '.join(nunca_s)}): a description nao dispara ou a skill nao e necessaria — ajuste ou remova.")
    L += ["## Sugestoes automaticas"] + ([f"- {s}" for s in sug] or ["- Nada evidente; rode de novo com mais dias de historico."])
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", default=".", help="pasta do projeto (padrao: atual)")
    ap.add_argument("--todos", action="store_true", help="analisa todos os projetos")
    ap.add_argument("--dias", type=int, default=30)
    a = ap.parse_args()

    base = pasta_projetos()
    if not base.is_dir():
        sys.exit(f"erro: historico nao encontrado em {base}")
    if a.todos:
        pastas, titulo = [p for p in base.iterdir() if p.is_dir()], "todos os projetos"
    else:
        alvo = codificar(Path(a.projeto))
        pastas = [p for p in base.iterdir() if p.is_dir() and p.name.lower() == alvo]
        titulo = Path(a.projeto).resolve().name
        if not pastas:
            sys.exit(f"erro: nenhum historico para {Path(a.projeto).resolve()} em {base}")
    limite = dt.datetime.now().timestamp() - a.dias * 86400
    arquivos = [f for p in pastas for f in p.rglob("*.jsonl") if f.stat().st_mtime >= limite]
    if not arquivos:
        sys.exit(f"nenhuma sessao nos ultimos {a.dias} dias")
    print(relatorio(analisar(arquivos), f"{titulo} (ultimos {a.dias} dias)"))


if __name__ == "__main__":
    main()
