"""
图片处理工具

提供缩略图生成等功能
"""
import base64
import io
from typing import Optional

from logging_config import get_logger

logger = get_logger(__name__)

# 缩略图默认尺寸
THUMBNAIL_SIZE = (200, 200)
THUMBNAIL_QUALITY = 85


def generate_thumbnail(
    image_base64: str,
    size: tuple[int, int] = THUMBNAIL_SIZE
) -> Optional[str]:
    """
    从 base64 编码的图片生成缩略图

    Args:
        image_base64: 原图的 base64 编码（可能包含 data:image/... 前缀）
        size: 缩略图尺寸，默认 (200, 200)

    Returns:
        缩略图的 base64 编码（不含前缀），失败返回 None
    """
    try:
        from PIL import Image

        # 去除可能的 data URL 前缀
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]

        # 解码 base64
        image_data = base64.b64decode(image_base64)

        # 打开图片
        image = Image.open(io.BytesIO(image_data))

        # 转换为 RGB（处理 RGBA 或其他模式）
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # 生成缩略图（保持比例）
        image.thumbnail(size, Image.Resampling.LANCZOS)

        # 保存为 JPEG 到内存
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=THUMBNAIL_QUALITY, optimize=True)
        buffer.seek(0)

        # 转为 base64
        thumbnail_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        logger.debug(
            f"Generated thumbnail: size={size}, "
            f"output_length={len(thumbnail_base64)} chars"
        )
        return thumbnail_base64

    except ImportError:
        logger.warning("Pillow not installed, cannot generate thumbnail")
        return None
    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {e}")
        return None


def get_thumbnail_data_url(thumbnail_base64: str) -> str:
    """
    将缩略图 base64 转换为 data URL 格式

    Args:
        thumbnail_base64: 缩略图的 base64 编码

    Returns:
        data:image/jpeg;base64,... 格式的字符串
    """
    return f"data:image/jpeg;base64,{thumbnail_base64}"
