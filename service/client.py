import zerorpc

c = zerorpc.Client(timeout=600000, heartbeat=600000)
c.connect("tcp://127.0.0.1:4242")

json_file = c.render_img('/home/anhmeo/Desktop/two people.psd')
json_file1 = c.render_img('/home/anhmeo/Desktop/dog1.psd')

for obj in json_file:
    print(obj)

for obj in json_file1:
    print(obj)
