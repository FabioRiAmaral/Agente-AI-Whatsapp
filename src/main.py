import logging, os, sys
import requests
from flask import Flask, request

app = Flask(__name__)

waha_url = "http://localhost:3000"