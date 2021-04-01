import zerorpc from "zerorpc"

var client = new zerorpc.Client({_heartbeatExpirationTime: 100000});
client.connect("tcp://127.0.0.1:4242");

client.invoke("render_img", "/home/anhmeo/Desktop/", function (error, res, more) {
    console.log(res);
});