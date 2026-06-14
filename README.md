# MOJO Carrot Codex Pet

一个 fan-made 的 Codex Desktop 自定义窗口宠物，把 Codex 的窗口宠物换成圆滚滚的 MOJO Carrot。

当前 v2 版本提取并转译了 `mojocarrot-on-desk` 的部分角色分层、状态映射和动作节奏，最终仍然是 Codex custom pet 使用的轻量 `8 x 9` spritesheet。这个仓库不包含 Electron 桌宠运行时、Agent hooks、后台服务或端口监听。

![Motion preview](previews/motion-preview.gif)

## Preview

![Contact sheet](previews/contact-sheet.png)

## Install

```bash
git clone https://github.com/xiaodinli2/mojo.git
cd mojo
./install.sh
```

Then restart Codex Desktop, or reload the app if your version supports reloading custom pets.

## Manual Install

Copy the `mojo-carrot` folder into your Codex pets directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/pets"
cp -R mojo-carrot "${CODEX_HOME:-$HOME/.codex}/pets/"
```

Then set this in `${CODEX_HOME:-$HOME/.codex}/config.toml`:

```toml
selected-avatar-id = "custom:mojo-carrot"
```

## Uninstall

```bash
./uninstall.sh
```

The uninstall script removes only the copied `mojo-carrot` pet folder. It does not edit your Codex config.

## Files

- `mojo-carrot/pet.json`: pet metadata
- `mojo-carrot/spritesheet.webp`: 8 x 9 transparent spritesheet
- `previews/contact-sheet.png`: full frame preview
- `previews/motion-preview.gif`: quick motion preview
- `docs/animation-mapping-v2.md`: v2 animation row mapping
- `tools/build-v2-from-mojocarrot-on-desk.py`: optional local generator for rebuilding v2 from a checked-out reference project

## Credits and Notice

This is an unofficial fan-made Codex pet for personal use. MOJO CARROT, 五月天/Mayday, and STAYREAL related names, character designs, and artwork belong to their respective rights holders. This repository is not affiliated with, endorsed by, or sponsored by 五月天/Mayday or STAYREAL.

The v2 motion mapping and generated spritesheet are informed by the public fan project [`lukelei2025/mojocarrot-on-desk`](https://github.com/lukelei2025/mojocarrot-on-desk), which itself credits [`rullerzhou-afk/clawd-on-desk`](https://github.com/rullerzhou-afk/clawd-on-desk). This project only packages a Codex custom-pet spritesheet and does not redistribute or run the Electron desktop-pet application.

Please do not use this project commercially unless you have permission from the relevant rights holders.

No separate open-source license is granted for the character artwork in this repository.
