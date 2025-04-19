from pymongo import MongoClient
from urllib.parse import quote_plus

class Database:
    def __init__(self):
        username = quote_plus("Nguyet2004")  # Lưu ý viết đúng tên tài khoản
        password = quote_plus("Nguyet1906")  # Mật khẩu
        uri = f"mongodb+srv://{username}:{password}@cluster0.09unx1q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        try:
            self.client = MongoClient(uri)
            self.db = self.client["TGMT"]
            print("✅ Kết nối MongoDB thành công!")
        except Exception as e:
            print(f"❌ Lỗi kết nối MongoDB: {e}")

    def save_statistic(self, player_name, score, level, mode):
        try:
            collection = self.db["statistics"]
            statistic = {
                "player_name": player_name,
                "score": score,
                "level": level,
                "mode": mode
            }
            collection.insert_one(statistic)
            print(f"✅ Lưu dữ liệu thành công: {statistic}")
        except Exception as e:
            print(f"❌ Lỗi khi lưu dữ liệu: {e}")

    def get_statistic(self):
        try:
            collection = self.db["statistics"]
            return list(collection.find())
        except Exception as e:
            print(f"❌ Lỗi khi lấy dữ liệu: {e}")
            return []

    def get_player_ranking(self, player_name):
        try:
            collection = self.db["statistics"]
            return list(collection.find({"player_name": player_name}))
        except Exception as e:
            print(f"❌ Lỗi khi lấy dữ liệu của {player_name}: {e}")
            return []