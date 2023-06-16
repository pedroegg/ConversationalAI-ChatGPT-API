import logging
import json
import os
import flask
from flask import request, render_template, redirect, Response
from cleantext import clean

import service.service as srv
import library.errors as errors

logger = logging.getLogger('Handler')

def GetTopics() -> Response:
    prompt = """
        List 5 random conversation topics that might be relevant to a Brazilian learner of English as a Second Language.
        Make at least 2 of them related to music industry, but not exacly about the music industry.
        Use simple vocabulary and a maximum of 1 word for each topic.
        For each topic, insert in the string a representative emoji to its left.
        The topics must be returned in pt-br language.
        Your response must be in the following JSON format: {{"topics": ["", "", "", "", ""]}}
    """

    for i in range(0, 3):
        try:
            content, _ = srv.AskChatGPT(
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.7,
            )

        except:
            raise

        try:
            obj = json.loads(content)
        except:
            continue

        if 'topics' in obj and isinstance(obj['topics'], list) and all(isinstance(elem, (str, bytes)) for elem in obj['topics']):
            break

    else:
        raise errors.OpenAiCommunicationError()

    res = flask.make_response()
    res.content_type = 'application/json; charset=utf-8'
    res.status_code = 200
    res.set_data(json.dumps({'topics': obj['topics']}))

    return res

def NewChat() -> Response:
    prompt = """
        You are a virtual learning assistant that helps Brazilian students practice English as a Second Language.
        Introduce yourself as "Lingui, the Letras Academy Chatbot" and start the conversation based on the chosen topic and English level.
        Make clear that your main goal is to help me get better in English and provide feedback on my performance.
        Use simple and direct language, and start the conversation by asking a question.
        You must always respond in English.
        Ask interesting questions to keep the conversation going. Avoid abstract questions.
        Do not ask me if i want something, just keep the conversation going talking about the topic.
        You can change subjects as long as the conversation stays related to the main theme.
        For every text i send you, you must:
        1 - Check if there is any grammatical, vocabulary, or semantic mistakes.
        2 - If it does, advice me and correct it on your response in a friendly manner.
        3 - Check if there is any typos.
        4 - If it does, advice me what is the correct way to write the word.
        Before you answer me, ensure that:
        1 - Your response is in english language.
        2 - You are giving me feedbacks of my mistakes.
        3 - You are asking interesting questions to keep the conversationg going.
        The chosen topic for this chat is {} and the chosen English level is {}. Keep the conversation appropriate to the topic and level.
    """

    promptAlteradoAntigo = """
        You are a virtual learning assistant chatbot that helps Brazilian students practice English as a Second Language.
        Introduce yourself as "Lingui, the Letras Academy Chatbot" and make clear that your main goal is to help me get better in English and provide feedback on my performance.
        You must always respond in english language.
        Use simple and direct language.
        You can start the conversation based on the provided pt-br topic and the provided English level, and then, ask a question.
        Throughout our conversation, you can present short fun facts related to the main topic, but don't do so in the first message or too often.
        Ask questions to keep the conversation going.
        You can change subjects as long as the conversation stays related to the main theme.
        Every time you ask a question, it should be the last thing in your message.
        As we chat, you should correct any language mistakes I might make. Do so in a friendly manner.
        You can also encourage me to ask for feedback on my English skills.
        Keep the conversation appropriate to the provided pt-br topic and level.
        Topic: {}.
        English level: {}.
    """

    promptLarissa = """
        You are a virtual learning assistant that helps Brazilian students practice English as a Second Language.
        Introduce yourself as the Letras Academy Chatbot and start the conversation based on the chosen topic and English level.
        Use simple and direct language, and start the conversation by asking a question.
        Throughout our conversation, you can present short fun facts related to the main topic, but don't do so in the first message or too often.
        Ask questions to keep the conversation going.
        You can change subjects as long as the conversation stays related to the main theme.
        Every time you ask a question, it should be the last thing in your message.
        As we chat, you should correct any language mistakes I might make.
        Do so in a friendly manner.
        You can also encourage me to ask for feedback on my English skills.
        The chosen topic for this chat is {}, and the chosen English level is {}. Keep the conversation appropriate to the topic and level.
    """

    if not request.is_json:
        raise errors.BadRequest('json inválido')

    data = request.get_json()
    if data is None:
        raise errors.BadRequest('json inválido')

    if not ('topic' in data and 'level' in data):
        raise errors.BadRequest('missing conversation topic or level fields')

    if not (isinstance(data['topic'], str) and isinstance(data['level'], str)):
        raise errors.BadRequest('invalid payload fields types')

    level = data['level'].lower()
    topic = data['topic'].lower()

    englishLevel = 'beginner (A1 and A2 of CEFR)'
    if level == os.getenv('PT_ENGLISH_LEVEL_INTERMEDIATE_TEXT'):
        englishLevel = 'intermediate (B1 and B2 of CEFR)'
    elif level == os.getenv('PT_ENGLISH_LEVEL_ADVANCED_TEXT'):
        englishLevel = 'advanced (B2 and C1 of CEFR)'

    try:
        englishTopic = srv.Translate(clean(topic, no_emoji=True))
    except:
        raise

    systemMessage = prompt.format(englishTopic, englishLevel)

    try:
        content, role = srv.AskChatGPT(
            messages=[{'role': 'user', 'content': 'hi'}, {'role': 'system', 'content': systemMessage}],
            #model=os.getenv('CHAT_GPT_4_MODEL'),
            temperature=0.7,
            max_tokens=200,
            useChain=False,
        )

    except:
        raise

    res = flask.make_response()
    res.content_type = 'application/json; charset=utf-8'
    res.status_code = 200
    res.set_data(json.dumps([
        {'content': systemMessage, 'role': 'system'},
        {'content': content, 'role': role},
    ]))

    return res

def ProcessMessage() -> Response:
    if not request.is_json:
        raise errors.BadRequest('json inválido')

    data = request.get_json()
    if data is None:
        raise errors.BadRequest('json inválido')

    if not 'messages' in data:
        raise errors.BadRequest('missing conversation messages')

    if not isinstance(data['messages'], list):
        raise errors.BadRequest('invalid payload message field type')

    lastUserMessage = ''
    for msg in data['messages']:
        if not isinstance(msg, dict):
            raise errors.BadRequest('invalid payload message field type')

        if not ('role' in msg and 'content' in msg):
            raise errors.BadRequest('messages list missing fields')

        if not (isinstance(msg['role'], str) and isinstance(msg['content'], str)):
            raise errors.BadRequest('invalid message list fields types')

        if msg['role'] not in ['system', 'user', 'assistant']:
            raise errors.BadRequest('one or more messages contains an invalid role')

        if msg['role'] == 'user':
            lastUserMessage = msg['content']


    corrections = srv.GetTextCorrections(lastUserMessage)
    if len(corrections) > 0:
        mistakeAdvice = ''
        for i, correction in enumerate(corrections):
            indexMsg = ''
            if len(corrections) > 1:
                indexMsg = '\n{} - '.format(i)

            mistakeAdvice += '{}Maybe the "{}" phrase was supposed to be "{}".'.format(indexMsg, correction['from'], correction['to'])

        print('RECOMENDANDO CORREÇÃO: {}'.format(mistakeAdvice))

        data['messages'].append({
            'role': 'system',
            'content': """
                Looks like there is some grammar or spelling mistakes in my last message: {}
                So now, please, give me a feedback about my mistake and explain how can i fix it.
            """.format(mistakeAdvice),
        })

    try:
        content, role = srv.AskChatGPT(
            messages=data['messages'],
            model=os.getenv('CHAT_GPT_3_16K_MODEL'),
            temperature=0.7,
            max_tokens=300,
            useChain=False,
        )

    except:
        raise

    res = flask.make_response()
    res.content_type = 'application/json; charset=utf-8'
    res.status_code = 200
    res.set_data(json.dumps({'content': content, 'role': role}))

    return res

def Translate():
    if not request.is_json:
        raise errors.BadRequest('json inválido')

    data = request.get_json()
    if data is None:
        raise errors.BadRequest('json inválido')

    if not 'text' in data:
        raise errors.BadRequest('missing text to translate')

    if not isinstance(data['text'], str):
        raise errors.BadRequest('invalid payload text field type')

    try:
        translation = srv.Translate(data['text'])
    except:
        raise

    res = flask.make_response()
    res.content_type = 'application/json; charset=utf-8'
    res.status_code = 200
    res.set_data(json.dumps({'translation': translation}))

    return res
