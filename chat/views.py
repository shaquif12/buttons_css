from django.shortcuts import render
import openai
import speech_recognition as sr
import pyttsx3

openai.api_key = "openaiapikey.txt"

with open("openaiapikey.txt", "r") as file:
    openai.api_key = file.read().strip()

r = sr.Recognizer()
mic = sr.Microphone(device_index=0)


def gpt3_completion(prompt, engine='text-davinci-002', temp=0.7, top_p=1.0, tokens=1000, freq_pen=0.0, pres_pen=0.0,
                     stop=None):
    prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temp,
        max_tokens=tokens,
        top_p=top_p,
        frequency_penalty=freq_pen,
        presence_penalty=pres_pen,
        stop=stop
    )
    text = response['choices'][0]['text'].strip()
    return text


def generate_response(conversation):
    text_block = '\n'.join(conversation)
    with open('prompt_chat.txt', 'r') as file:
        prompt = file.read().replace('<<BLOCK>>', text_block)
    response = gpt3_completion(prompt, stop=None)

    # Remove "bot:" prefix if present
    if response.startswith('BOT:'):
        response = response[4:]  # Remove the first 4 characters (i.e., "bot:")
        
       # Remove "?" prefix if present 
    if response.startswith('?'):
        response = response[1:] # Remove the first characters (i.e., "?") 
        
       # Remove "is your job BOT:"  prfix if present
    if response.startswith('is your job BOT:'):
        response = response[16:]  # Remove first 16 characters (i.e., "is your job BOT:")  
        
        # Remove "FARM ASSISTANT:"
    if response.startswith('FARM ASSISTANT:'):
        response = response[14:]  # Remove the first 14 character (i.e., "FARM ASSISTANT") 
        
        # Remove "" prefix if present
    if response.startswith('? FARMAI:'):
        response = response[8:] # remove the first eight character (i.e., "")
            
    # Remove "FARM ASSISTANT" prefix if present
    if response.startswith('FARM ASSISTANT:'):
        response = response[16:]  # Remove the first 16 characters (i.e., "FARM ASSISTANT:")
    
    # Remove "doing today FARMAI" prefix if present
    if response.startswith('doing today FARMAI'):
        response = response[18:] # Remove the first 18 characters (i.e., "doing today FARMAI") 
    if response.startswith('FARM AI'):
        response = response[7:] # Remove the first 18 characters (i.e., "doing today FARMAI") 
    if response.startswith('I ASSISTANT'):
        response = response[16:] # Remove the first 18 characters (i.e., "doing today FARMAI") 
    if response.startswith('ASSISTANT:'):
        response = response[10:]
    if response.startswith('Farm AI Assistant:'):
        response = response[10:]

         

    conversation.append(response)
    return response


def chat_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')

        conversation = []
        conversation.append('USER: %s' % user_input)

        if 'voice' in request.POST:
            # Voice recognition
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source)
                try:
                    user_voice_input = r.recognize_google(audio)
                    if user_voice_input:
                        conversation.append('USER (voice): %s' % user_voice_input)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass
        else:
            # Text input
            conversation.append('USER: %s' % user_input)

        response = generate_response(conversation)

        if 'voice' in request.POST:
            # Text-to-speech
            engine = pyttsx3.init()
            engine.setProperty('voice', 'hi')
            engine.say(response)
            engine.runAndWait()

        return render(request, 'chat.html', {'response': response})

    return render(request, 'chat.html')