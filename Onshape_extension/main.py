from src.config import API_KEY, API_SECRET_KEY
from parse_variables_txt import parse_variable_file

print(API_KEY)
print(API_SECRET_KEY)
print("Config loaded successfully")



fall_back = parse_variable_file("sspg_equations.txt")
print(fall_back)

print(type(fall_back))
