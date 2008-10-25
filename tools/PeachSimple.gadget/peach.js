/*
#
# Copyright (c) 2008 Blake Frantz & Michael Eddington
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in	
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# Authors:
#	Blake Frantz(blakefrantz@gmail.com)
#
# $Id$
*/

var g_timer;
var g_errorCount = 0;
var g_errorThreshold = 3;
var g_url = "http://127.0.0.1:9001/?gadgetData";
var g_xhr;
var g_maxStrLen = 12;

function truncate(str)
{

	var maxLen = g_maxStrLen;
			
	if(str.length >= g_maxStrLen)
	{
		str = str.substr(0, maxLen) + "...";

		return str;
	}
	else
	{
		return str;
	}
}

function updateGadget()
{
	try
	{	
		if(g_xhr)
		{
			if (g_xhr.statusText == 'OK')
			{	
				var dataElements = g_xhr.responseText.split(",");
			
				runName.innerHTML = truncate(dataElements[0]);
			
				if(dataElements[1].length == 0)
				{
					statusBox.innerHTML = "<font color=#5aff12>Complete</font>";
				}
				else
				{
					statusBox.innerHTML = "Running";
				}

				testName.innerHTML = truncate(dataElements[1]);
				currentTest.innerHTML = dataElements[2];
				totalTests.innerHTML = dataElements[3];
				faultCount.innerHTML = dataElements[4];						

				g_errorCount = 0;
			} 
		}

	}
	catch(e)
	{
		g_errorCount++;

		if(g_errorCount > g_errorThreshold)
		{
			g_errorCount = 0;
			resetGadget();
		}
	}
}

function resetGadget()
{
	runName.innerHTML = "-";
	testName.innerHTML = "-";
	currentTest.innerHTML = "-";
	totalTests.innerHTML = "-";
	faultCount.innerHTML = "-";
	statusBox.innerHTML = "-";
}

function init()
{
	if (window.XMLHttpRequest)
	{
		g_timer = window.setInterval("getStats();", 3000);
	}	
}

function getStats()
{
	var randomNumber=Math.floor(Math.random()*30000);

	try
	{
		g_xhr = new XMLHttpRequest();	
		g_xhr.onreadystatechange = updateGadget;
		g_xhr.open("GET", g_url + randomNumber + '');
		g_xhr.send();
	}
	catch(e)
	{
		g_errorCount++;

		if(g_errorCount > g_errorThreshold)
		{
			g_errorCount = 0;
			resetGadget();
		}
	}

}




