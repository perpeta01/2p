from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import time
import threading
import logging
from flask import Flask, render_template, jsonify

logging.basicConfig(filename='mines_bot.log', level=logging.INFO)

app = Flask(__name__)

class MinesBot:
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.block_stats = {i: 0 for i in range(25)}
        self.bet_interval = 180  # Intervalo padrão de 3 minutos

    def start_browser(self):
        if self.driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            self.driver = webdriver.Chrome(options=options)
            self.driver.get('https://blaze.com/pt/games/mines')
            print("Por favor, faça login manualmente.")

    def place_bet(self):
        previously_chosen = set()
        while self.is_running:
            try:
                start_bet_button = self.driver.find_element(By.XPATH, '//*[@id="mine-controller"]/div[1]/div/button')
                start_bet_button.click()
                time.sleep(1)

                blocks = [self.driver.find_element(By.ID, f"{i}") for i in range(25)]
                blocks_to_open = random.randint(2, 4)

                # Escolhe blocos com maior probabilidade de não ter bombas
                weighted_blocks = sorted(self.block_stats, key=self.block_stats.get, reverse=True)
                chosen_blocks = random.sample(weighted_blocks[:10], blocks_to_open)

                chosen_blocks = [block for block in chosen_blocks if block not in previously_chosen]
                previously_chosen.update(chosen_blocks)

                for block_id in chosen_blocks:
                    block = self.driver.find_element(By.ID, f"{block_id}")
                    block.click()
                    time.sleep(1)

                bomb_detected = False
                for block_id in chosen_blocks:
                    block = self.driver.find_element(By.ID, f"{block_id}")
                    try:
                        bomb_icon = block.find_element(By.XPATH, './/img[@alt="bombs"]')
                        if bomb_icon.is_displayed():
                            bomb_detected = True
                            self.block_stats[block_id] -= 1
                            break
                    except:
                        self.block_stats[block_id] += 1

                if not bomb_detected:
                    start_bet_button.click()

                time.sleep(self.bet_interval)
            except Exception as e:
                logging.error(f"Erro ao apostar: {e}")
                time.sleep(5)

    def start_auto_betting(self):
        self.is_running = True
        self.place_bet()

    def stop_auto_betting(self):
        self.is_running = False

bot = MinesBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    threading.Thread(target=bot.start_browser).start()
    return jsonify({"status": "Browser started. Please log in."})

@app.route('/start_betting', methods=['POST'])
def start_betting():
    threading.Thread(target=bot.start_auto_betting).start()
    return jsonify({"status": "Betting started."})

@app.route('/stop_betting', methods=['POST'])
def stop_betting():
    bot.stop_auto_betting()
    return jsonify({"status": "Betting stopped."})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
