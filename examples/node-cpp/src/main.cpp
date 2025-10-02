#include <chrono>
#include <iostream>
#include <thread>

int main() {
  std::cout << "[example-cpp] starting..." << std::endl;
  int i = 0;
  while (true) {
    std::cout << "[example-cpp] tick " << i++ << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(1));
  }
  return 0;
}
