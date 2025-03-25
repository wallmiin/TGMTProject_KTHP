from pymongo import MongoClient
from urllib.parse import quote_plus

class Database:
    def __init__(self):
        username = quote_plus("Nguyet04")  # Mã hóa username
        password = quote_plus("Nguyet1906")  # Mã hóa password
        uri = f"mongodb+srv://{username}:{password}@cluster0.5wunr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
        try:
            self.myClient = MongoClient(uri)
            self.db = self.myClient["game_db"]  # Thay "game_db" bằng tên database của bạn
            print("✅ Kết nối MongoDB thành công.")
        except Exception as e:
            print(f"❌ Lỗi kết nối MongoDB: {e}")

    def get_statistic(self):
        try:
            collection = self.db["statistics"]  # Thay "statistics" bằng collection của bạn
            return list(collection.find())
        except Exception as e:
            print(f"❌ Lỗi khi lấy dữ liệu: {e}")
            return []

    def save_statistic(self, player_name, score, level, mode):
        try:
            collection = self.db["statistics"]
            item_details = self.get_statistic()  # Kiểm tra trước khi lưu
            
            data = {
                "player_name": player_name,
                "score": score,
                "level": level,
                "mode": mode
            }
            collection.insert_one(data)
            print("✅ Dữ liệu đã được lưu vào MongoDB.")
        except Exception as e:
            print(f"❌ Lỗi khi lưu dữ liệu: {e}")

