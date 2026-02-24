import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO
import mysecretkeys

from mysecretkeys import YAweather_key

# Настройки темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WeatherBusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Home Dashboard")
        self.geometry("1280x1024")

        # Данные API Яндекс.Погоды. Эти переменные находятся в файле mysecretkeys.py
        self.weather_key = mysecretkeys.YAweather_key
        self.lat = mysecretkeys.YAlat
        self.lon = mysecretkeys.YAlon
        self.headers = {'X-Yandex-Weather-Key': self.weather_key}

        self.setup_ui()
        self.refresh_weather()
        self.refresh_bus()

    def get_icon(self, icon_name, size=100):
        url = f"https://yastatic.net/weather/i/icons/confident/dark/64/{icon_name}.png"
        try:
            resp = requests.get(url, timeout=5)
            return ctk.CTkImage(Image.open(BytesIO(resp.content)), size=(size, size))
        except:
            return None

    def setup_ui(self):
        # --- СЕКЦИЯ ПОГОДЫ ---
        self.weather_frame = ctk.CTkFrame(self, corner_radius=30, fg_color="#1a1c1e")
        self.weather_frame.pack(pady=20, padx=30, fill="both", expand=True)

        # Текущая погода
        self.current_frame = ctk.CTkFrame(self.weather_frame, fg_color="transparent")
        self.current_frame.pack(pady=30, fill="x")

        self.main_icon_label = ctk.CTkLabel(self.current_frame, text="")
        self.main_icon_label.pack(side="left", padx=(100, 40))

        self.temp_main = ctk.CTkLabel(self.current_frame, text="--°", font=("Arial", 160, "bold"))
        self.temp_main.pack(side="left")

        # Блок подробностей
        self.details_grid = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        self.details_grid.pack(side="right", padx=100)

        self.det_feels = self.create_detail_label(self.details_grid, "ОЩУЩАЕТСЯ", 0)
        self.det_hum = self.create_detail_label(self.details_grid, "ВЛАЖНОСТЬ", 1)
        self.det_wind = self.create_detail_label(self.details_grid, "ВЕТЕР / ПОРЫВЫ", 2)

        # Прогноз
        self.forecast_container = ctk.CTkFrame(self.weather_frame, fg_color="transparent")
        self.forecast_container.pack(fill="x", padx=50, pady=20)

        # --- СЕКЦИЯ ТРАНСПОРТА ---
        self.bus_frame = ctk.CTkFrame(self, corner_radius=30, fg_color="#1a1c1e")
        self.bus_frame.pack(pady=(0, 20), padx=30, fill="both", expand=True)

        ctk.CTkLabel(self.bus_frame, text="РАСПИСАНИЕ АВТОБУСОВ", font=("Arial", 24, "bold"),
                     text_color="#2ecc71").pack(pady=20)

        self.bus_container = ctk.CTkFrame(self.bus_frame, fg_color="transparent")
        self.bus_container.pack(fill="both", expand=True, padx=40)

    def create_detail_label(self, master, title, row):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.grid(row=row, column=0, sticky="e", pady=5)
        ctk.CTkLabel(f, text=title, font=("Arial", 14, "bold"), text_color="gray").pack(side="left", padx=10)
        lbl = ctk.CTkLabel(f, text="--", font=("Arial", 24, "bold"))
        lbl.pack(side="left")
        return lbl

    def refresh_weather(self):
        # 1. Погода
        # это заглушка для тестирования. Яндекс Погода отдает не более 30 вызовов в сутки или типа того. Для тестирования этого мало
        # поэтому надо сделать какой-то mock-сервис.
        data = requests.get(f"http://192.168.1.11:8089/v2/forecast?lat={self.lat}&lon={self.lon}", headers=self.headers, timeout=10).json()
        # это вызов яндекс-погоды. После отладки поменять вызов мока на этот
        # data = requests.get(f"https://api.weather.yandex.ru/v2/forecast?lat={self.lat}&lon={self.lon}",
        #                     headers=self.headers, timeout=10).json()

        fact = data['fact']
        self.temp_main.configure(text=f"{fact['temp']}°")
        self.det_feels.configure(text=f"{fact['feels_like']}°")
        self.det_hum.configure(text=f"{fact['humidity']}%")
        self.det_wind.configure(text=f"{fact['wind_speed']} / {fact['wind_gust']} м/с")

        main_icon = self.get_icon(fact['icon'], size=200)
        if main_icon: self.main_icon_label.configure(image=main_icon)

        # Прогноз на _сегодня_
        for widget in self.forecast_container.winfo_children(): widget.destroy()
        tomorrow = data['forecasts'][0]['parts']
        for name, key in [("Ночь", "night"), ("Утро", "morning"), ("День", "day"), ("Вечер", "evening")]:
            card = ctk.CTkFrame(self.forecast_container, fg_color="#252a30", corner_radius=20, height=250)
            card.pack(side="left", expand=True, padx=10, fill="both")
            ctk.CTkLabel(card, text=name, font=("Arial", 18, "bold")).pack(pady=10)
            icon = self.get_icon(tomorrow[key]['icon'], size=80)
            if icon: ctk.CTkLabel(card, image=icon, text="").pack()
            avg_t = tomorrow[key]['temp_avg']
            ctk.CTkLabel(card, text=f"{avg_t}°", font=("Arial", 36, "bold")).pack(pady=15)

        self.after(4000000, self.refresh_weather)
        # except:
        #     pass

    def refresh_bus(self):

        for widget in self.bus_container.winfo_children(): widget.destroy()

# начало вставки ------------------------------------
        bus_configs = [
            {"stop_id": "9eef8eb8-8601-461b-a00a-583c88569436", "num": "155", "stop": "Печальный проезд",
             "dest": "Полежаевская", "times": [], "telemetry": []},
            {"stop_id": "4ceef0fa-51d8-4a75-8f8d-1b0d620a3a74", "num": "294", "stop": "Шелепихинское шоссе",
             "dest": "Полежаевская", "times": [], "telemetry": []},
            {"stop_id": "3a2ac10d-3037-49fe-a0f1-d2ace0888564", "num": "315", "stop": "Шелепихинский мост",
             "dest": "Филёвская пойма", "times": [], "telemetry": []}
        ]

        # Вызов Московского транспорта не работает с "User-Agent": "Python что-то там"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
        }

        for item in bus_configs:
            try:
                # 1. Выполняем запрос к API
                url = f"https://moscowtransport.app/api/stop_v2/{item['stop_id']}"
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Проверка на ошибки HTTP
                stop_data = response.json()

                # 2. Ищем нужный маршрут в списке routePath по номеру автобуса
                # Очищаем times, telemetry перед заполнением на случай повторного запуска
                item['times'] = []
                item['telemetry'] = []

                found_route = None
                for route in stop_data.get('routePath', []):
                    if route.get('number') == item['num']:
                        found_route = route
                        break

                # 3. Если маршрут найден, берем первые 3 значения времени (индексы 0, 1, 2)
                if found_route:
                    forecasts = found_route.get('externalForecast', [])
                    # Срез [:3] автоматически берет "не более 3-х", даже если их меньше
                    for forecast in forecasts[:3]:
                        if 'time' in forecast:
                            item['times'].append(forecast['time'] // 60)
                            item['telemetry'].append(forecast['byTelemetry'])

            except Exception as e:
                print(f"Ошибка при обработке остановки {item['stop_id']} (автобус {item['num']}): {e}")
# конец вставки ------------------------------------

        for bus in bus_configs:
            row = ctk.CTkFrame(self.bus_container, fg_color="#252a30", corner_radius=20, height=110)
            # row = ctk.CTkFrame(self.bus_container, fg_color="#252a30", corner_radius=20, height=180)
            row.pack(fill="x", pady=10)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=bus['num'], font=("Arial", 40, "bold"), width=150, height=80,
                         fg_color="#3b8ed0", corner_radius=10).pack(side="left", padx=30)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", padx=20)
            ctk.CTkLabel(info, text=bus['stop'], font=("Arial", 22, "bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"в сторону: {bus['dest']}", font=("Arial", 16), text_color="gray").pack(anchor="w")

            times_f = ctk.CTkFrame(row, fg_color="transparent")
            times_f.pack(side="right", padx=50)
            # for t in bus['times']:
            #     ctk.CTkLabel(times_f, text=f"{t} мин", font=("Arial", 28, "bold"),
            #                  text_color="#2ecc71" if t < 10 else "white", width=120).pack(side="left", padx=10)
            for t, tele in zip(bus['times'], bus['telemetry']):
                ctk.CTkLabel(times_f, text=f"{t} мин", font=("Arial", 28, "bold"),
                             text_color="#2ecc71" if tele else "white", width=120).pack(side="left", padx=10)

        # Обновление: погода раз в час, транспорт раз в 30 сек (через отдельные таймеры в реальном приложении)
        self.after(60000, self.refresh_bus)


if __name__ == "__main__":
    app = WeatherBusApp()
    app.mainloop()

