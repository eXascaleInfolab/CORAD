def sort(line, content, counter):
    temp = line.split(',')
    temp[len(temp) - 1] = temp[len(temp) - 1].rstrip('\n')
    if counter != 0:
        time_1 = temp[0].split(' ')
        time = []
        time = time_1[0].split('-') + time_1[1].split(':')
        temp[0] = list(map(int, time))
        temp[1:3] = list(map(int, temp[1:3]))
    content.append(temp)
                                 
        
def display(filename):
    f = open(filename, 'r')
    """
    List organisation is designed as:
    [['time','power (W)','energy (Wh)'],[[2018, 1, 1, 5, 0, 0], 0, 78],...]
    """
    content = []
    counter = 0
    for line in f:
        sort(line, content,counter)
        counter = counter + 1
    f.close()
    print(content)
