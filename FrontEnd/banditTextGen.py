
import logging
import requests
import html
import os.path
from datetime import datetime

class textGen:
    #textGenHost="localhost:5000"
    #Address to AWS outside RMIT network
    #textGenHost='52.62.118.55:7860'
    #address within RMIT network
    textGenHost='ec2-54-79-118-186.ap-southeast-2.compute.amazonaws.com:7860'
    lastResponse = None
    history = {'internal': [], 'visible': []}

    logger = logging.getLogger('textgen')
    logger.setLevel(logging.DEBUG)

    
    logPath = f"{os.path.dirname(os.path.abspath(__file__))}/logs"
    if not os.path.exists(logPath):
        os.makedirs(logPath)
        
    logName = f"log-{datetime.today().strftime('%Y-%m-%d')}"
    logFile = os.path.abspath(f"{logPath}/{logName}.log")
    fh = logging.FileHandler(logFile)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s- %(message)s'))
    logger.addHandler(fh)
        

    def textGen(self, input):
        self.logger.info(f'User: {input}')
        request = {
            'user_input': input,
            'max_new_tokens': 250,
            'auto_max_new_tokens': False,
            'max_tokens_second': 0,
            'history': self.history,
            'mode': 'chat',  # Valid options: 'chat', 'chat-instruct', 'instruct'
            'character': 'Rosie',
            'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
            'your_name': 'You',
            'regenerate': False,
            '_continue': False,
            'chat_instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',

            # Generation params. If 'preset' is set to different than 'None', the values
            # in presets/preset-name.yaml are used instead of the individual numbers.
            'preset': 'None',
            'do_sample': True,
            'temperature': 0.7,
            'top_p': 0.1,
            'typical_p': 1,
            'epsilon_cutoff': 0,  # In units of 1e-4
            'eta_cutoff': 0,  # In units of 1e-4
            'tfs': 1,
            'top_a': 0,
            'repetition_penalty': 1.18,
            'repetition_penalty_range': 0,
            'top_k': 40,
            'min_length': 0,
            'no_repeat_ngram_size': 0,
            'num_beams': 1,
            'penalty_alpha': 0,
            'length_penalty': 1,
            'early_stopping': False,
            'mirostat_mode': 0,
            'mirostat_tau': 5,
            'mirostat_eta': 0.1,
            'guidance_scale': 1,
            'negative_prompt': '',

            'seed': -1,
            'add_bos_token': True,
            'truncation_length': 2048,
            'ban_eos_token': False,
            'custom_token_bans': '',
            'skip_special_tokens': True,
            'stopping_strings': []
        }

        

        try:
            response = requests.post(f"http://{self.textGenHost}/api/v1/chat", json=request)
            response.raise_for_status()
        except requests.HTTPError as ex:
            message = f'HTTP Error: {response.status_code} {response.reason}'
            self.logger.error(message)
            print(message)
        except Exception as ex:
            self.logger.error(ex)
            print(ex)
        else:
            result = html.unescape(response.json()['results'][0]['history']['visible'][-1][1])
            self.history =  response.json()['results'][0]['history']
            self.lastResponse = result
            self.logger.info(f'Rosie: {result}')
            return result

        

if __name__ == '__main__':
    txt = textGen()
    while(True):
        try:
            print("Rosie: " + txt.textGen(input("You: ")))
        except TypeError:
            print("Rosie could not respond")
        except KeyboardInterrupt:
            break
