import pickle
user = input('User Name:')
f = open('./../user/' + user + '/' + user + '.idx','rb')
# print(f)
ans = pickle.load(f)
print('Msgs:', ans.msgs, '\n')
print('Index', ans.index)
