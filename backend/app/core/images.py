import io

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_SIDE = 512
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def prepare_photo(file: UploadFile) -> bytes:
    """আপলোড করা ছবি যাচাই করে ছোট JPEG বানিয়ে ফেরত দেয়"""
    raw = file.file.read(MAX_UPLOAD_BYTES + 1)

    if not raw:
        raise HTTPException(status_code=400, detail="ফাইলটি ফাঁকা")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="ছবি সর্বোচ্চ ৫ MB হতে পারবে")

    try:
        with Image.open(io.BytesIO(raw)) as img:
            if img.format not in ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=415,
                    detail="শুধু JPG, PNG বা WebP ছবি দেওয়া যাবে",
                )

            img = ImageOps.exif_transpose(img)  # ফোনের ঘোরানো ছবি সোজা করা

            if img.mode != "RGB":  # স্বচ্ছ অংশ সাদা করে দেওয়া
                rgba = img.convert("RGBA")
                background = Image.new("RGB", rgba.size, (255, 255, 255))
                background.paste(rgba, mask=rgba.getchannel("A"))
                img = background

            img.thumbnail((MAX_SIDE, MAX_SIDE))

            out = io.BytesIO()
            img.save(out, format="JPEG", quality=85, optimize=True)
            return out.getvalue()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(status_code=400, detail="এটি বৈধ ছবি নয়")