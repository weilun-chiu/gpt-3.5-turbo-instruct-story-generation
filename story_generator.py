import openai
import time
import threading
from contextlib import contextmanager

# get an openai api key from here: https://platform.openai.com/account/api-keys
openai.api_key = "<your openai api key>"

def rm_return_doublequote(s):
    s = s.replace('\n\n', ' ')
    s = s.replace('\n', ' ')
    s = s.replace('\"', '')
    return s.strip()

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def time_limit(seconds, msg=''):
    
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out for operation {}".format(msg))
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()

# engine selection:
# optimized for dialogue: gpt-3.5-turbo	
# single-turn instructions: text-davinci-003
# expert model but expensive: gpt-4
def query_openai(inputs_with_prompts, 
                 engine='text-davinci-002', # $0.0200 / 1K tokens
                 max_tokens=500, 
                 num_sequence=1, 
                 temp=0,
                 retry=2):
  
  completions = {"choices": []}
  complete = False
  for i in range(retry):
    try:
      with time_limit(20, 'run gpt-3'):
        completions = openai.Completion.create(
          engine=engine, 
          max_tokens=max_tokens, 
          prompt=inputs_with_prompts, 
          temperature=temp, 
          n=num_sequence, # num of returned sequence
        )
        complete = True
        break
    except:
      time.sleep(2)
  if not complete:
    return False

  outputs = [c["text"] for c in completions["choices"]]
  
  return outputs
  
def answer_question(question, simulation_data, retry=2):
    
    numFails = 0
    while numFails < retry:
      ret = query_openai(f'Read the following json format file and reply the question. \n\n question: {question} \n\n simulation: {simulation_data}')
      if ret == False:
        numFails += 1
      else:
        break
    if ret == False:
      return f'Due to API limitations, please reduce the number of simulation rounds when asking questions as the simulated data has exceeded the cache capacity.'
    
    if type(ret) == list:
      ret = ret[0]
      
    ret = rm_return_doublequote(ret)
    return ret
  
if __name__ == '__main__':
  simulation_data = "{\
  \"simulation_1\": [\
    {\"time\": \"0\", \"speed\": \"0\"},\
    {\"time\": \"1\", \"speed\": \"30\"},\
    {\"time\": \"2\", \"speed\": \"60\"},\
    {\"time\": \"3\", \"speed\": \"90\"},\
    {\"time\": \"4\", \"speed\": \"120\"},\
    {\"time\": \"5\", \"speed\": \"150\"},\
    {\"time\": \"6\", \"speed\": \"180\"},\
    {\"time\": \"7\", \"speed\": \"210\"},\
    {\"time\": \"8\", \"speed\": \"240\"},\
    {\"time\": \"9\", \"speed\": \"270\"},\
    {\"time\": \"10\", \"speed\": \"300\"},\
    {\"time\": \"11\", \"speed\": \"330\"},\
    {\"time\": \"12\", \"speed\": \"360\"},\
    {\"time\": \"13\", \"speed\": \"390\"},\
    {\"time\": \"14\", \"speed\": \"420\"}\
  ],\
  \"simulation_2\": [\
    {\"time\": \"0\", \"speed\": \"0\"},\
    {\"time\": \"1\", \"speed\": \"40\"},\
    {\"time\": \"2\", \"speed\": \"80\"},\
    {\"time\": \"3\", \"speed\": \"120\"},\
    {\"time\": \"4\", \"speed\": \"160\"},\
    {\"time\": \"5\", \"speed\": \"200\"},\
    {\"time\": \"6\", \"speed\": \"240\"},\
    {\"time\": \"7\", \"speed\": \"280\"},\
    {\"time\": \"8\", \"speed\": \"320\"},\
    {\"time\": \"9\", \"speed\": \"360\"},\
    {\"time\": \"10\", \"speed\": \"400\"},\
    {\"time\": \"11\", \"speed\": \"440\"},\
    {\"time\": \"12\", \"speed\": \"480\"},\
    {\"time\": \"13\", \"speed\": \"520\"},\
    {\"time\": \"14\", \"speed\": \"560\"}\
  ],\
  \"simulation_3\": [\
    {\"time\": \"0\", \"speed\": \"0\"},\
    {\"time\": \"1\", \"speed\": \"50\"},\
    {\"time\": \"2\", \"speed\": \"100\"},\
    {\"time\": \"3\", \"speed\": \"150\"},\
    {\"time\": \"4\", \"speed\": \"200\"},\
    {\"time\": \"5\", \"speed\": \"250\"},\
    {\"time\": \"6\", \"speed\": \"300\"},\
    {\"time\": \"7\", \"speed\": \"350\"},\
    {\"time\": \"8\", \"speed\": \"400\"},\
    {\"time\": \"9\", \"speed\": \"450\"},\
    {\"time\": \"10\", \"speed\": \"500\"},\
    {\"time\": \"11\", \"speed\": \"550\"},\
    {\"time\": \"12\", \"speed\": \"600\"},\
    {\"time\": \"13\", \"speed\": \"650\"},\
    {\"time\": \"14\", \"speed\": \"700\"}\
  ]\
  }"
  print(answer_question('List the average of maximum speed in recent three runs.', simulation_data))
  # answer should be "The average of maximum speed in recent three runs is 400."
    
    
