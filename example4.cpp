//
// example4.cpp
//
// This is a 'bare-bone' example of a TMQM client written in C++. 
//
// This is the same program as example2.py, except I ran it 
// through a Python to c++ converter.
//
// For documentation see:
//   https://www.gsw7.net/files/tmqm/readme.md
//


#include <iostream>
#include <string>
#include <fstream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>


int main() {

// Get the IP address of the Host.
std::string filename = "TMQM-HostIP.txt"; // Created by setup.py
std::string hostIP = "";
if (std::ifstream(filename)) {
  std::ifstream file(filename);
  std::getline(file, hostIP);
}


// Example of sending a message.
std::string m = "send,public,noReply,This is a test message sent to 'public'.";
int sock = socket(AF_INET, SOCK_STREAM, 0);
struct sockaddr_in server;
server.sin_family = AF_INET;
server.sin_port = htons(65432);
server.sin_addr.s_addr = inet_addr(hostIP.c_str());
if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
  std::cout << "Connection failed" << std::endl;
  return 1;
}
send(sock, m.c_str(), m.length(), 0);
char reply[1024] = {0};
recv(sock, reply, 1024, 0);
close(sock);
std::cout << reply << "\n";


// Recieve all messages in the queue.
// This will include messages that were sent BEFORE
//   this script started, but have not yet expired. 
std::string Index = "0";
std::string To = "";
std::string From = "";
std::string Text = "";
while (To != "None") {
  int sock = socket(AF_INET, SOCK_STREAM, 0);
  struct sockaddr_in server;
  server.sin_addr.s_addr = inet_addr(hostIP.c_str());
  server.sin_family = AF_INET;
  server.sin_port = htons(65432);
  if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
    std::cout << "Connection failed" << "\n";
    return 1;
  }
  std::string message = "recv," + Index;
  send(sock, message.c_str(), message.length(), 0);
  char reply[1024];
  recv(sock, reply, 1024, 0);
  close(sock);
  std::string reply_str(reply);
  std::cout << reply << "\n";
  Index = reply_str.substr(0, reply_str.find(","));
  reply_str.erase(0, reply_str.find(",") + 1);
  To = reply_str.substr(0, reply_str.find(","));
  reply_str.erase(0, reply_str.find(",") + 1);
  From = reply_str.substr(0, reply_str.find(","));
  reply_str.erase(0, reply_str.find(",") + 1);
  Text = reply_str;
}  

}
// End of code.

