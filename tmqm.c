#include <sys/socket.h> 
#include <netinet/in.h> 
#include <cstdlib> 
#include <iostream> 
#include <unistd.h> 
#include <string>
#include <algorithm>
#include <ctime>
#include <map>
#include <cstring>
#include <arpa/inet.h>
#include <iostream>

// ****************************************************************************
// Tinny Message Queue Manager ( tmqm.cpp ).
// Version 4.0.0
// Written by Joseph Roten, 2023/06/29
//
// This program, hereafter called the 'Host', will allow Client programs
//   to send/broadcast text messages and data between each other.
//
// Clients can be written in different programing languages, 
//  and running on different devices ( Linux,Windows,Mac,Arduino,EXP32,etc. )
//  connected to the same network segment ( same WiFi router ).
//
// Messages are deleted from the Queue after 10 minutes to free up memory.
// The max number of Clients is unlimited.
// The max number of messages is only limited by available memory.
// The max number of channels is unlimited.
//
// This work is licensed under the Creative Commons Attribution 4.0 International License. 
// To view a copy of this license, 
// visit http://creativecommons.org/licenses/by/4.0/ 
// or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
//
// You are free to use this file in your own projects as long as you follow a
// few simple rules. See license above for details. 
// 
// For documentation see:
//   https://www.gsw7.net/files/tmqm/README.html
// 
// To compile the program from source code: 
//    Linux:      g++ tmqm.cpp -o tmqm
//    Windows:    gcc tmqm.c -o tmqm.exe
//
// ****************************************************************************

const std::string WHITESPACE = " \n\r\t\f\v";

// Function to remove whitespaces from the left side of the string. 
std::string ltrim(const std::string &s){
  size_t start = s.find_first_not_of(WHITESPACE);
  return (start == std::string::npos) ? "" : s.substr(start);
  }

// Function to remove whitespaces from the right side of the string. 
std::string rtrim(const std::string &s){
  size_t end = s.find_last_not_of(WHITESPACE);
  return (end == std::string::npos) ? "" : s.substr(0, end + 1);
  }
 
// Function to remove whitespaces from both sides of the string. 
std::string trim(const std::string &s) {
  return rtrim(ltrim(s));
  }

int main() {

  std::map<int, std::string> MessageQueue;
  std::map<int, int> TimeQueue;
  int counter1 = 0;
  int topIndex = 0;
  int bottomIndex = 1;
  int c = 0;
  int i = 0;
  std::string k = "";

  // Display credits.
  std::cout << "Tinny Message Queue Manager (tmqm)\n";
  std::cout << "Version 4.0.0\n\n";
  std::cout << "This program will allow Client programs\n";
  std::cout << "  to send text messages between each other.\n\n";
  std::cout << "For documentation see:\n";
  std::cout << "  https://www.gsw7.net/files/tmqm/readme.md\n\n";   

  // There should always be at least one message in the queue.
  MessageQueue.insert( {0, "None,None,++Blank" });
  TimeQueue.insert( { 0, time(NULL) } );

  // Create a socket (IPv4, TCP)
  int sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd == -1) {
    std::cout << "Failed to create socket. errno: " << errno << std::endl;
    exit(EXIT_FAILURE);
  }

  // Listen to port 65432 for incomming requests.
  sockaddr_in sockaddr;
  sockaddr.sin_family = AF_INET;
  sockaddr.sin_addr.s_addr = INADDR_ANY;
  sockaddr.sin_port = htons(65432);
  if (bind(sockfd, (struct sockaddr*)&sockaddr, sizeof(sockaddr)) < 0) {
    std::cout << "Failed to bind to port 65432. errno: " << errno << std::endl;
    exit(EXIT_FAILURE);
  }

  // Start listening.
  if (listen(sockfd, 10) < 0) {
    std::cout << "Failed to listen on socket. errno: " << errno << std::endl;
    exit(EXIT_FAILURE);
  }

  std::cout << "The Message Queue Manager (Host) is now running.\n";

  // Start of loop.
  while ( 1==1 ){

    // Open a connection.
    auto addrlen = sizeof(sockaddr);
    int connection = accept(sockfd, (struct sockaddr*)&sockaddr, (socklen_t*)&addrlen);
    if (connection >= 0) {
    
      // Read from the connection
      char buffer[1024];
      auto bytesRead = read(connection, buffer, 1024);
      std::string mess(buffer,bytesRead);
      std::string message = trim( mess );
      
      // Define the default reply.
      std::string reply = "Error\n";
      
      // Delete top messages in the queue, if it has expired.
      // Messages will expire after 10 minutes of having been sent.
      // This will help free up memory.
      if ( ( bottomIndex - topIndex ) > 5 ){
        if ( TimeQueue[topIndex] < ( time(NULL) - 600 ) ){
          TimeQueue.erase(topIndex);
          MessageQueue.erase(topIndex);
          ++topIndex;
        }      
      } 
      
      // If the length of the message is greater than 5 characters.
      if ( message.length() > 5 ) {

        // Proc any 'send' messages.
        if (message.rfind("send,", 0) == 0) {
          MessageQueue.insert({bottomIndex, trim( message.substr(5) ) });
          TimeQueue.insert({bottomIndex, time(NULL) });
          ++bottomIndex;
          reply = "OK\n";
        } 

        // Proc any 'recv' messages.
        if (message.rfind("recv,", 0) == 0) {
          c = 0;
          k = trim( message.substr(5) );
          for (char w : k) {
            if (w >= '0' && w <= '9') { c = c * 10 + (w - '0'); }
          }  
          reply = std::to_string(c) + ",None,None,None\n";
          c = c + 1 ;
          if ( c < topIndex ) { c = topIndex ; }
          if ( MessageQueue.count(c) > 0 ) { 
            reply = std::to_string(c) + ',' + MessageQueue[c] + "\n";
            }  
        } 
         
       } // End of   'if ( message.length > 5 )'

      // Proc any 'init' request.
      if (message.rfind("init", 0) == 0) {
        reply = std::to_string(counter1) + "," + std::to_string(bottomIndex - 1) + "," + inet_ntoa(sockaddr.sin_addr) + "\n";
        ++counter1;
      }
      
      // Proc any 'helo' request.
      if (message.rfind("helo", 0) == 0) {
        reply = "Queue Manager Responding.\n";
      }

      // Send a reply back to the client & Close the connections
      send(connection, reply.c_str(), reply.size(), 0);
      close(connection);

    }  // End of   if(connection >= 0)
  
  } // End of while loop.  
  
  close(sockfd);  // Close the socket.

}  // End of main()

// End of code.

