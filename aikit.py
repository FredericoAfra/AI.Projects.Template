#!/usr/bin/env python3
"""aikit - instala o AI.Projects.Template em projetos.

  aikit install [pasta] [--profile core|ralph|devcontainer|full] [--marketplace github|local] [--dry-run]
  aikit update  [pasta]   reaplica a versao atual sem sobrescrever o que voce editou
  aikit status  [pasta]   versao instalada e arquivos editados
  aikit validate          confere skills, agentes e JSONs do kit

Skills e agentes vem do plugin 'ai-kit' (o projeto so declara o marketplace no
.claude/settings.json). O instalador copia apenas os arquivos do projeto.
So usa a biblioteca padrao do Python 3.8+.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
VERSION = (KIT / "VERSION").read_text(encoding="utf-8").strip()
PLUGIN = KIT / "plugins" / "ai-kit"
MARKETPLACE, PLUGIN_NAME, GITHUB_REPO = "ai-projects-template", "ai-kit", "FredericoAfra/AI.Projects.Template"
MANIFEST = ".ai-kit/manifest.json"
PROFILES = {"core": ["core"], "ralph": ["core", "ralph"], "devcontainer": ["core", "devcontainer"],
            "full": ["core", "ralph", "devcontainer"]}
PROJECT_OWNED = {"AGENTS.md", "CLAUDE.md"}  # criados uma vez, nunca sobrescritos
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()[:16]


def die(msg: str) -> None:
    sys.exit(f"erro: {msg}")


def load_manifest(target: Path) -> dict:
    p = target / MANIFEST
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if kv:
            out[kv.group(1)] = kv.group(2).strip().strip("\"'")
    return out


def deep_merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        elif isinstance(v, list) and isinstance(out.get(k), list):
            out[k] = out[k] + [x for x in v if x not in out[k]]
        elif k not in out:
            out[k] = v
    return out


class Writer:
    """Grava arquivos rastreando o hash: na atualizacao, arquivo editado pelo usuario
    nao e sobrescrito; a versao nova vai para <arquivo>.aikit-new."""

    def __init__(self, target: Path, dry: bool):
        self.target, self.dry = target, dry
        self.manifest = load_manifest(target)
        self.files = dict(self.manifest.get("files", {}))
        self.log = {"criado": [], "atualizado": [], "conflito": [], "mantido": [], "igual": []}

    def put(self, dest: Path, data: bytes) -> None:
        if not self.dry:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)

    def write(self, rel: str, data: bytes) -> None:
        dest, new, owned = self.target / rel, sha(data), rel in PROJECT_OWNED
        if not dest.exists():
            self.put(dest, data)
            self.log["criado"].append(rel)
            if not owned:
                self.files[rel] = new
            return
        cur = sha(dest.read_bytes())
        if cur == new:
            self.log["igual"].append(rel)
        elif owned:
            self.log["mantido"].append(rel)
        elif self.files.get(rel) == cur:
            self.put(dest, data)
            self.log["atualizado"].append(rel)
            self.files[rel] = new
        else:
            self.put(dest.with_name(dest.name + ".aikit-new"), data)
            self.log["conflito"].append(rel)

    def save(self, **extra) -> None:
        self.manifest.update(extra, kitVersion=VERSION, files=dict(sorted(self.files.items())),
                             updatedAt=_dt.datetime.now().isoformat(timespec="seconds"))
        if not self.dry:
            p = self.target / MANIFEST
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(self.manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def report(self, title: str) -> None:
        print(f"\n== {title}{' (simulacao: nada gravado)' if self.dry else ''}")
        for k, label in [("criado", "criados"), ("atualizado", "atualizados"),
                         ("conflito", "CONFLITOS - voce editou; versao nova salva como .aikit-new"),
                         ("mantido", "mantidos (arquivos do projeto)")]:
            if self.log[k]:
                print(f"  {label}:\n" + "\n".join(f"    - {f}" for f in self.log[k]))
        print(f"  sem mudanca: {len(self.log['igual'])}")


def settings(w: Writer, marketplace: str) -> None:
    rel = ".claude/settings.json"
    base = json.loads((KIT / "kit/core/.claude/settings.json").read_text(encoding="utf-8"))
    src = {"source": "directory", "path": str(KIT)} if marketplace == "local" else {"source": "github", "repo": GITHUB_REPO}
    base["extraKnownMarketplaces"] = {MARKETPLACE: {"source": src}}
    base["enabledPlugins"] = {f"{PLUGIN_NAME}@{MARKETPLACE}": True}
    dest = w.target / rel
    try:
        cur = json.loads(dest.read_text(encoding="utf-8") or "{}") if dest.exists() else {}
    except json.JSONDecodeError:
        w.log["conflito"].append(rel + " (JSON invalido; nao alterado)")
        return
    merged = deep_merge(cur, base)
    merged["extraKnownMarketplaces"][MARKETPLACE] = base["extraKnownMarketplaces"][MARKETPLACE]
    data = (json.dumps(merged, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if dest.exists() and sha(dest.read_bytes()) == sha(data):
        w.log["igual"].append(rel)
    else:
        w.log["atualizado" if dest.exists() else "criado"].append(rel + (" (mesclado)" if dest.exists() else ""))
        w.put(dest, data)


def install(target: Path, profile: str, marketplace: str, dry: bool, update: bool = False) -> None:
    if not target.is_dir():
        die(f"pasta nao encontrada: {target}")
    if target == KIT:
        die("o destino e o proprio kit; informe a pasta de outro projeto")
    if profile not in PROFILES:
        die(f"perfil invalido: {profile} ({', '.join(PROFILES)})")
    w = Writer(target, dry)
    for part in PROFILES[profile]:
        root = KIT / "kit" / part
        for src in sorted(p for p in root.rglob("*") if p.is_file()):
            rel = src.relative_to(root).as_posix()
            if rel == ".claude/settings.json":
                continue
            data = src.read_bytes()
            if rel.endswith(".md"):
                data = data.decode("utf-8").replace("{{PROJECT_NAME}}", target.name).encode("utf-8")
            w.write(rel, data)
    claude_md = target / "CLAUDE.md"
    if claude_md.exists() and "@AGENTS.md" not in claude_md.read_text(encoding="utf-8"):
        w.put(claude_md, ("@AGENTS.md\n\n" + claude_md.read_text(encoding="utf-8")).encode("utf-8"))
        w.log["mantido"] = [f for f in w.log["mantido"] if f != "CLAUDE.md"]
        w.log["atualizado"].append("CLAUDE.md (+ @AGENTS.md no topo)")
    settings(w, marketplace)
    w.save(profile=profile, marketplace=marketplace)
    w.report(f"{'Atualizacao' if update else 'Instalacao'} do ai-kit {VERSION} em {target}")
    if not update:
        src = GITHUB_REPO if marketplace == "github" else KIT
        print(f"\nProximos passos:\n  - Preencha AGENTS.md (visao geral, comandos, regras do projeto).\n"
              f"  - Abra o Claude Code na pasta e aceite instalar o plugin ai-kit\n"
              f"    (ou: /plugin marketplace add {src}  e  /plugin install {PLUGIN_NAME}@{MARKETPLACE}).\n"
              f"  - Comece com /ai-kit:planejar.")


def cmd_install(a) -> None:
    install(Path(a.target).resolve(), a.profile, a.marketplace, a.dry_run)


def cmd_update(a) -> None:
    t = Path(a.target).resolve()
    m = load_manifest(t) or die("projeto sem .ai-kit/manifest.json; rode 'aikit install'")
    print(f"Instalado: {m.get('kitVersion')}  ->  kit atual: {VERSION}")
    install(t, m.get("profile", "core"), m.get("marketplace", "github"), a.dry_run, update=True)


def cmd_status(a) -> None:
    t = Path(a.target).resolve()
    m = load_manifest(t) or die("projeto sem .ai-kit/manifest.json")
    files = m.get("files", {})
    changed = [f for f, h in files.items() if (t / f).exists() and sha((t / f).read_bytes()) != h]
    missing = [f for f in files if not (t / f).exists()]
    print(f"{t}\n  kit {m.get('kitVersion')} (atual {VERSION}) · perfil {m.get('profile')} · plugin via {m.get('marketplace')}")
    print(f"  rastreados: {len(files)} · editados: {len(changed)} · removidos: {len(missing)}")
    for f in changed:
        print(f"    ~ {f}")
    for f in missing:
        print(f"    - {f}")
    for p in t.rglob("*.aikit-new"):
        print(f"    ! conflito pendente: {p.relative_to(t).as_posix()}")


def cmd_validate(a) -> None:
    errs = []
    for p in sorted(PLUGIN.glob("skills/*/SKILL.md")):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("name") != p.parent.name or not NAME_RE.match(p.parent.name):
            errs.append(f"{p}: name deve ser igual a pasta ({p.parent.name})")
        if not fm.get("description") or len(fm["description"]) > 1024:
            errs.append(f"{p}: description ausente ou > 1024 caracteres")
    for p in sorted(PLUGIN.glob("agents/*.md")):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("name") != p.stem:
            errs.append(f"{p}: name deve ser igual ao arquivo ({p.stem})")
        if not fm.get("description"):
            errs.append(f"{p}: description ausente")
        if fm.get("effort") and fm["effort"] not in ("low", "medium", "high", "xhigh", "max"):
            errs.append(f"{p}: effort invalido")
    for j in [KIT / ".claude-plugin/marketplace.json", PLUGIN / ".claude-plugin/plugin.json", KIT / "kit/core/.claude/settings.json"]:
        try:
            json.loads(j.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            errs.append(f"{j}: JSON invalido ({e})")
    versions = {VERSION, json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8")).get("version")}
    if len(versions) > 1:
        errs.append(f"versoes diferentes entre VERSION e plugin.json: {versions}")
    if errs:
        print("\n".join(f"- {e}" for e in errs))
        sys.exit(1)
    skills = len(list(PLUGIN.glob("skills/*/SKILL.md")))
    agents = len(list(PLUGIN.glob("agents/*.md")))
    print(f"OK: {skills} skills, {agents} agentes, JSONs validos (versao {VERSION})")


def main() -> None:
    ap = argparse.ArgumentParser(prog="aikit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"aikit {VERSION}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("install", help="instala o kit em um projeto")
    p.add_argument("target", nargs="?", default=".")
    p.add_argument("--profile", default="core", help="core | ralph | devcontainer | full")
    p.add_argument("--marketplace", choices=["github", "local"], default="github",
                   help="origem do plugin: repositorio no GitHub ou esta pasta local")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_install)
    p = sub.add_parser("update", help="atualiza para a versao atual do kit")
    p.add_argument("target", nargs="?", default=".")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_update)
    p = sub.add_parser("status", help="versao instalada e arquivos editados")
    p.add_argument("target", nargs="?", default=".")
    p.set_defaults(fn=cmd_status)
    p = sub.add_parser("validate", help="valida o kit")
    p.set_defaults(fn=cmd_validate)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
