#include <iostream>
#include "json.hpp"
#include "HTTPRequest.hpp"

using json = nlohmann::json;
using namespace std;

int main()
{
    http::Request request("http://localhost:3000/getAllPairs");

    const http::Response response = request.send("GET");

    json j = json::parse(response.body);
    cout << j << endl;

    cout << endl;

    cout << j["close_XMR,USDT"] << endl;

    return 0;
}