#!/bin/bash

# example of a script that sets up necessary environment variables permanently

vars=(
  RAPID_API_KEY
  TWITTER_ACCESS_TOKEN
  TWITTER_ACCESS_SECRET
  TWITTER_CONSUMER_KEY
  TWITTER_CONSUMER_SECRET
  IO_USERNAME
  IO_KEY
)

keys=(
  placeholder
  placeholder
  placeholder
  placeholder
  placeholder
  placeholder
  placeholder
)

for ((i=0;i<${#vars[@]};++i)); do
    sudo -H sed -i "s/${vars[i]}=.*\n//g" /etc/environment
    echo "${vars[i]}='${keys[i]}'" | sudo tee -a /etc/environment
done

source ~/.bashrc
