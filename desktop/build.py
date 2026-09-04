# -*- coding: utf-8 -*-
r"""
COMPOUND.OS · Windows 便携版构建脚本

一键完成：
1. 准备 renderer 目录（index.html + news.json）
2. 生成程序图标（assets/rose.ico）
3. 使用 PyInstaller --onedir --windowed 打包
4. 验证关键资源存在
5. 创建桌面快捷方式
6. 压缩为 ZIP 完整包

用法：
    python desktop/build.py

输出：
    E:\workbuddy\...\COMPOUND.OS\dist\COMPOUND.OS\COMPOUND.OS.exe
    E:\workbuddy\...\COMPOUND.OS\dist\COMPOUND.OS.zip
    桌面快捷方式：COMPOUND.OS.lnk
"""

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


# ---------- 项目路径 ----------
ROOT = Path(__file__).resolve().parent.parent
DESKTOP_DIR = ROOT / "desktop"
ASSETS_DIR = DESKTOP_DIR / "assets"
RENDERER_DIR = DESKTOP_DIR / "renderer"
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"

EXE_NAME = "COMPOUND.OS"
APP_NAME = "COMPOUND.OS"


def run(cmd, **kwargs):
    print(f"\n[RUN] {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kwargs)


def ensure_icon():
    """用 Pillow 生成一枚简单的金色玫瑰图标（256x256 ico）。"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    ico_path = ASSETS_DIR / "rose.ico"
    png_path = ASSETS_DIR / "rose.png"

    if ico_path.exists():
        print(f"[ICON] 已存在: {ico_path}")
        return str(ico_path)

    try:
        from PIL import Image, ImageDraw
    except ImportError as e:
        raise RuntimeError("缺少 Pillow，请先安装：pip install Pillow") from e

    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 金色渐变背景圆（由中心向外模拟）
    for r in range(size // 2, 0, -1):
        ratio = r / (size // 2)
        # 金色 #D4AF37 -> 浅金 #F9E79F
        c = int(212 * ratio + 249 * (1 - ratio))
        m = int(175 * ratio + 231 * (1 - ratio))
        y = int(55 * ratio + 159 * (1 - ratio))
        draw.ellipse((size // 2 - r, size // 2 - r, size // 2 + r, size // 2 + r), fill=(c, m, y, 255))

    # 简单玫瑰花瓣（同心圆叠加，深金描边）
    cx, cy = size // 2, size // 2
    petal_color = (139, 69, 19, 200)
    outline = (101, 67, 33, 255)
    for i, (rx, ry, angle) in enumerate([(60, 70, 0), (50, 60, 45), (40, 50, 0)]):
        # 仅画椭圆模拟花瓣层
        box = (cx - rx, cy - ry + i * 8, cx + rx, cy + ry + i * 8)
        draw.ellipse(box, fill=petal_color, outline=outline, width=2)

    # 保存 PNG 与 ICO
    img.save(png_path, "PNG")
    img.save(ico_path, "ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

    print(f"[ICON] 生成: {ico_path}")
    return str(ico_path)


def prepare_renderer():
    """将网页源码与默认资讯复制到 desktop/renderer，供 PyInstaller 打包。"""
    if RENDERER_DIR.exists():
        shutil.rmtree(RENDERER_DIR)
    RENDERER_DIR.mkdir(parents=True)

    src_html = ROOT / "index.html"
    src_news = ROOT / "news.json"
    dst_html = RENDERER_DIR / "index.html"
    dst_news = RENDERER_DIR / "news.json"

    shutil.copy2(src_html, dst_html)
    if src_news.exists():
        shutil.copy2(src_news, dst_news)

    print(f"[COPY] {src_html.name} -> {dst_html}")
    print(f"[COPY] {src_news.name} -> {dst_news}")


def run_pyinstaller(icon_path: str):
    """调用 PyInstaller 生成单目录可执行文件。"""
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    main_py = DESKTOP_DIR / "main.py"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--name={EXE_NAME}",
        f"--icon={icon_path}",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--specpath={BUILD_DIR}",
        f"--add-data={RENDERER_DIR}{os.pathsep}renderer",
        f"--add-data={ASSETS_DIR}{os.pathsep}assets",
        str(main_py),
    ]

    run(cmd, cwd=str(ROOT))


def verify_bundle():
    """检查打包产物是否包含关键资源。"""
    app_dir = DIST_DIR / EXE_NAME
    exe = app_dir / f"{EXE_NAME}.exe"
    internal_renderer = app_dir / "_internal" / "renderer" / "index.html"
    internal_news = app_dir / "_internal" / "renderer" / "news.json"

    assert exe.exists(), f"缺少 EXE: {exe}"
    assert internal_renderer.exists(), f"缺少 renderer/index.html: {internal_renderer}"
    assert internal_news.exists(), f"缺少 renderer/news.json: {internal_news}"

    print(f"[VERIFY] EXE: {exe}")
    print(f"[VERIFY] renderer/index.html: {internal_renderer}")
    print(f"[VERIFY] renderer/news.json: {internal_news}")


def create_desktop_shortcut():
    """在 Windows 桌面创建指向 EXE 的快捷方式。"""
    exe_path = DIST_DIR / EXE_NAME / f"{EXE_NAME}.exe"
    icon_path = ASSETS_DIR / "rose.ico"
    desktop = Path.home() / "Desktop"
    lnk_path = desktop / f"{APP_NAME}.lnk"

    if not exe_path.exists():
        print(f"[WARN] 找不到 EXE，跳过快捷方式: {exe_path}")
        return None

    # 用 PowerShell 创建 .lnk
    ps = (
        "$ws = New-Object -ComObject WScript.Shell; "
        f"$sc = $ws.CreateShortcut('{lnk_path}'); "
        f"$sc.TargetPath = '{exe_path}'; "
        f"$sc.WorkingDirectory = '{exe_path.parent}'; "
        f"$sc.IconLocation = '{icon_path}'; "
        "$sc.Save(); "
        f"Write-Host 'Shortcut saved to {lnk_path}'"
    )

    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            check=True,
            text=True,
        )
        print(f"[SHORTCUT] {lnk_path}")
        return str(lnk_path)
    except subprocess.CalledProcessError as e:
        print(f"[WARN] 创建桌面快捷方式失败: {e}")
        return None


def zip_bundle():
    """将完整程序目录打包为 ZIP（保留目录结构）。"""
    app_dir = DIST_DIR / EXE_NAME
    zip_path = DIST_DIR / f"{EXE_NAME}.zip"

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                abs_path = Path(root) / file
                arcname = str(abs_path.relative_to(DIST_DIR))
                zf.write(abs_path, arcname)

    print(f"[ZIP] {zip_path}")
    return str(zip_path)


def main():
    print("=" * 60)
    print(" COMPOUND.OS Windows 便携版构建")
    print("=" * 60)

    # 1. 生成图标
    icon_path = ensure_icon()

    # 2. 准备 renderer
    prepare_renderer()

    # 3. 打包
    run_pyinstaller(icon_path)

    # 4. 验证
    verify_bundle()

    # 5. 创建桌面快捷方式
    create_desktop_shortcut()

    # 6. 压缩
    zip_path = zip_bundle()

    print("\n" + "=" * 60)
    print(" 构建完成")
    print("=" * 60)
    print(f" 程序目录: {DIST_DIR / EXE_NAME}")
    print(f" 压缩包:   {zip_path}")
    print(f" 快捷方式: {Path.home() / 'Desktop' / f'{APP_NAME}.lnk'}")
    print("\n 提示：首次运行请确保系统已安装 Microsoft Edge WebView2 Runtime。")
    print("=" * 60)


if __name__ == "__main__":
    main()
