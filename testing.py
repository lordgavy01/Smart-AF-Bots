# dict={} 
# dict['Model1']=[5,100,]

num_Agents=[60]
from subprocess import call

# sys.stdout = open('output.txt','a')

for i in range(len(num_Agents)):
    call(["python3", "window.py",str(i)])

"""
    for keys in dict:
    
"""