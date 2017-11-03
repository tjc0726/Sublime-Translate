import sublime
import sublime_plugin
import hashlib
import urllib
import random
import threading
import json

class TranslateTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = self.view.sel()
        s = sublime.load_settings("Translate.sublime-settings")
        translate_whole_word = s.get("translate_whole_word", False)
        appKey = s.get("appKey", "")
        secretKey = s.get("secretKey", "")
        for sel in sels:
            if translate_whole_word:
                wholeWord = self.view.word(sel)
                words = self.view.substr(wholeWord)
            else:
                words = self.view.substr(sel)
            # print(words)
            if words != '':
                thread = YouDaoApiCall(words, appKey, secretKey, 5)
                thread.start()


class TranslateInputCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        sels = self.view.sel()
        sublime.active_window().show_input_panel('希望是个好东西，生生不息，遥不可及 :)', 'enjoy everyday！', self.on_done, None, self.on_cancel)

    def on_done(self, words):
        if words != '':
            s = sublime.load_settings("Translate.sublime-settings")
            appKey = s.get("appKey", "")
            secretKey = s.get("secretKey", "")
            thread = YouDaoApiCall(words, appKey, secretKey, 5)
            thread.start()
    def on_cancel():
        pass

class YouDaoApiCall(threading.Thread):

    def __init__(self, words, appKey, secretKey, timeout):
        self.words = words
        self.appKey = appKey
        self.secretKey = secretKey
        self.timeout = timeout
        threading.Thread.__init__(self)

    def run(self):
        appKey = self.appKey
        secretKey = self.secretKey
        myurl = 'https://openapi.youdao.com/api'
        q = self.words
        fromLang = 'auto'
        toLang = 'auto'
        salt = random.randint(1, 65536)

        sign = appKey+q+str(salt)+secretKey
        sign = hashlib.md5(sign.encode('utf-8')).hexdigest()
        myurl = myurl+'?appKey='+appKey+'&q='+urllib.parse.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign

        try:
            conn = urllib.request.urlopen(myurl, timeout=self.timeout)
            response = conn.read()
            result = response.decode('utf-8')
            self.parse(result)
            return
        except Exception as e:
            sublime.error_message(str(e))
        finally:
            conn.close()

    def parse(self, result):
        jsonObj = json.loads(result)
        try:
            resArr = jsonObj['basic']['explains']
        except Exception as e:
            resArr = ['/(ㄒoㄒ)/~~ 未找到释义']
        finally:
            sublime.active_window().show_quick_panel(resArr, self.on_select)

    def on_select(self, index):
        # if index > -1:
        #     sublime.message_dialog(str(index))
        pass
