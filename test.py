import re
import json

mixtral_data = str({"questions": ["The potential number of seats in Delta Center after renovation for hockey is 17,500. This is stated when Ryan Smith says, 'The plan is to expand that number to roughly 17,500.'", "What pick are the Giants trading to move up in the draft?", "Who is the administration's pick for quarterback in New York?", "What type of deal did the Giants give Drew Lock in March?", "What type of player does the Giants' new brainstrust hope to acquire?"],"short_answer_questions": ["Who is the current quarterback for the New York Giants?", "What picks are the Giants trading?", "Who did the Giants sign in March?"],"answer_choices": [["Daniel Jones", "Drew Lock", "Baker Mayfield", "Jimmy Garoppolo"], ["First Round", "Second Round", "Third Round", "Fourth Round"], ["Daniel Jones", "Drew Lock", "Bryce Young", "C.J. Stroud"], ["Veteran Deal", "Rookie Deal", "Trade Deal", "Free Agent Deal"], ["Franchise Quarterback", "Running Back", "Wide Receiver", "Offensive Lineman"]],"correct_answers": ["Daniel Jones", "Second Round", "Not specified", "Veteran Deal", "Franchise Quarterback"]})
mixtral_data = re.sub("'", '"', mixtral_data)
print(mixtral_data)
print()
invalid_char_pattern = r"[^a-zA-Z0-9\s,{}[]:.\-\'\"!@#$%^&*()]"
mixtral_data = re.sub(r"\\", "", mixtral_data)
remove_pattern = r'([a-zA-Z])"([^\],:])' 
remove_pattern2 = r'([a-zA-Z])"([a-zA-Z])' # remove contractions i.e. I can't
remove_pattern3 = r'(?<!, |\{\s|\[\s)(?<!\{|\[|\n)(?<!", )"([^",.:\]| ]])'
remove_pattern4 = r'(?<!", |\], )(?<!\{|\[)"([a-zA-Z])' 

mixtral_data = re.sub(r'\"\"', '', mixtral_data)
mixtral_data = re.sub(r'\n', '', mixtral_data)
mixtral_data = re.sub(r'\s+', ' ', mixtral_data)
mixtral_data = re.sub(remove_pattern, r'\1\2', mixtral_data)
mixtral_data = re.sub(remove_pattern2, r"\1\2", mixtral_data)
mixtral_data = re.sub(remove_pattern3, r"\1", mixtral_data)
mixtral_data = re.sub(remove_pattern4, r"\1", mixtral_data)

# Use re.sub() to remove all invalid characters
cleaned_string = re.sub(invalid_char_pattern, "", mixtral_data)

# Print the cleaned string
print(cleaned_string)
print()
mixtral_data = json.loads(mixtral_data)
print(mixtral_data)
print(type(mixtral_data))

