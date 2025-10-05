import os
import json
import time
import requests
from ddgs import DDGS
from PIL import Image
from io import BytesIO

# Загружаем JSON
with open("goods.json", "r", encoding="utf-8") as f:
    goods = json.load(f)

# Папка для сохранения картинок
save_dir = r"C:\Users\filfo\source\repos\Nail_shop.ru\Nail_shop\images"
os.makedirs(save_dir, exist_ok=True)

# Лог ошибок
error_log = open("errors.log", "w", encoding="utf-8")

# Целевой размер
TARGET_WIDTH = 1360
TARGET_HEIGHT = 2048
TOLERANCE = 50  # допустимое отклонение

with DDGS() as ddgs:
    for gid, item in goods.items():
        query = item["name"] + " guitar"
        filename = item["img"]
        filepath = os.path.join(save_dir, filename)

        success = False
        try:
            # Берём до 10 результатов
            results = ddgs.images(query, max_results=100, size="Large")

            for res in results:
                url = res.get("image")
                try:
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200 and r.content:
                        img = Image.open(BytesIO(r.content))

                        # Проверяем размеры
                        if (TARGET_WIDTH - TOLERANCE <= img.width <= TARGET_WIDTH + TOLERANCE and
                            TARGET_HEIGHT - TOLERANCE <= img.height <= TARGET_HEIGHT + TOLERANCE):
                            # Если размеры подходят — сохраняем
                            img = img.convert("RGB")
                            img.save(filepath, "PNG")
                            print(f"✅ {item['name']} → {filename} ({img.width}x{img.height})")
                            success = True
                            break

                        # Если картинка больше — обрезаем
                        elif img.width >= TARGET_WIDTH and img.height >= TARGET_HEIGHT:
                            left = (img.width - TARGET_WIDTH) // 2
                            top = (img.height - TARGET_HEIGHT) // 2
                            right = left + TARGET_WIDTH
                            bottom = top + TARGET_HEIGHT
                            cropped = img.crop((left, top, right, bottom))
                            cropped = cropped.convert("RGB")
                            cropped.save(filepath, "PNG")
                            print(f"✂️ {item['name']} → {filename} (обрезано {img.width}x{img.height} → {TARGET_WIDTH}x{TARGET_HEIGHT})")
                            success = True
                            break

                except Exception:
                    continue  # пробуем следующую ссылку

            if not success:
                msg = f"❌ Не удалось найти подходящую картинку для {item['name']}\n"
                print(msg.strip())
                error_log.write(msg)

        except Exception as e:
            msg = f"Ошибка для {item['name']}: {e}\n"
            print(msg.strip())
            error_log.write(msg)

        time.sleep(1)  # пауза, чтобы не словить блокировку

error_log.close()
