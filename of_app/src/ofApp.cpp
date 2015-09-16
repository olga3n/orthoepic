#include "ofApp.h"
#include "ofxTCPClient.h"

#define STRINGIFY(A) #A

//--------------------------------------------------------------
void ofApp::setup(){

	//--- network ----------------------------------------------
	
	connected = tcpClient.setup("127.0.0.1", 12345);
	tcpClient.setMessageDelimiter("\n");

	tcpClient_opt.setup("127.0.0.1", 12345);
	tcpClient_opt.setMessageDelimiter("\n");

	connectTime = 0;
	deltaTime = 0;

	tcpClient.send("1");
	tcpClient_opt.send("1");

	//--- sound ------------------------------------------------

	string path = "."; 
	dir.allowExt("mp3");
	dir.listDir(path);

	for(int i = 0; i < dir.numFiles(); i++)
	{
		ofLogNotice(dir.getPath(i));
	}

	sound = 0;
	volume = 0.4f;

	mySound.loadSound(dir.getPath(sound));
	mySound.play();
	mySound.setVolume(volume);

	//--- video ------------------------------------------------

	w = 426;
	h = 320;

	vidGrabber.setDeviceID(0); //choose your destiny
	vidGrabber.initGrabber(w, h);

	N = 4;
	fboList = new ofFbo[N];
	fboHSVList = new ofFbo[4];
	fboRGBList = new ofFbo[4];
	blobOptions = new int *[N];

	for (int i = 0; i < N; ++i)
	{
		blobOptions[i] = new int[2];
		blobOptions[i][0] = 213; blobOptions[i][1] = 160;

		fboList[i].allocate(w, h);
		fboHSVList[i].allocate(w, h);
		fboRGBList[i].allocate(w, h);
	}

	cameraFbo.allocate(w, h);

	//--- threshold filter

	string shaderProgram = STRINGIFY
	(
		uniform sampler2DRect pict;
		
		uniform float min_a;
		uniform float min_b;
		uniform float min_c;

		uniform float max_a;
		uniform float max_b;
		uniform float max_c;

		void main (void)
		{
			vec2 pos = gl_TexCoord[0].st;
			vec3 pix = texture2DRect(pict, pos).rgb;

			int a = 1; int b = 1; int c = 1;

			if((min_a < max_a && (pix[0] > max_a / 255.0 || pix[0] < min_a / 255.0) 
				|| (min_a > max_a && ( pix[0] > max_a / 255.0 && pix[0] < min_a / 255.0 ))))
			{
				a = 0;
			}

			if((min_b < max_b && (pix[1] > max_b / 255.0 || pix[1] < min_b / 255.0) 
				|| (min_b > max_b && ( pix[1] > max_b / 255.0 && pix[1] < min_b / 255.0 ))))
			{
				b = 0;
			}

			if((min_c < max_c && (pix[2] > max_c / 255.0 || pix[2] < min_c / 255.0) 
				|| (min_c > max_c && ( pix[2] > max_c / 255.0 && pix[2] < min_c / 255.0 ))))
			{
				c = 0;
			}

			if ( a == 0 || b == 0 || c == 0 )
			{
				gl_FragColor = vec4(0.0, 0.0, 0.0, 1);
			}
			else
			{
				gl_FragColor = vec4(1.0, 1.0, 1.0, 1);
			}
		}
	);

	shader.setupShaderFromSource(GL_FRAGMENT_SHADER, shaderProgram);
	shader.linkProgram();

	//--- data -------------------------------------------------

	values = new float [N];
	new_values = new float [N];
	time_ = new int [N];

	for (int i = 0; i < N; ++i) 
	{
		values[i] = 0.5f;
		new_values[i] = 0.5f;

		time_[i] = -1;
	} 

	type = 1;
	value = 0.3f;

	values[(int)type] = value;

	eps = 0.04f;

	//--- interface --------------------------------------------

	MODE = 1;
	MODE_SOUND = 1;

	poemFont.loadFont("Comfortaa-Regular.ttf", 46, true, true);
	optFont.loadFont("Comfortaa-Regular.ttf", 30, true, true);
	newFont.loadFont("Comfortaa-Regular.ttf", 30, true, true);
	smallFont.loadFont("Comfortaa-Regular.ttf", 14, true, true);

	for (int i = 0; i < 4; ++i)
	{
		gui[i].setup("mode-min-max");
		gui[i].add(toggles[i].setup("hsv", false));

		gui[i].add(slider[i].setup("min-1", 0, 0, 255));
		gui[i].add(slider[i + 4].setup("min-2", 0, 0, 255));
		gui[i].add(slider[i + 8].setup("min-3", 0, 0, 255));
		
		gui[i].add(slider[i + 12].setup("max-1", 255, 0, 255));
		gui[i].add(slider[i + 16].setup("max-2", 255, 0, 255));
		gui[i].add(slider[i + 20].setup("max-3", 255, 0, 255));

		gui[i].setPosition(80 + 440 * i, 750);
	}

	cameraimg.allocate(w, h);

	gui_0.setup();
	gui_0.add(toggle_MODE_COLOR.setup("HSV", true));
	gui_0.setPosition(90, 55);

	gui[0].loadFromFile("set0.xml");
	gui[1].loadFromFile("set1.xml");
	gui[2].loadFromFile("set2.xml");
	gui[3].loadFromFile("set3.xml");
}

//--------------------------------------------------------------
void ofApp::update(){

	//--- data -------------------------------------------------

	char* type_bytes = (char *)(&type);
	char* value_bytes = (char *)(&value);

	//--- network ----------------------------------------------

	deltaTime = ofGetElapsedTimeMillis() - connectTime;

	if(connected) {
		if (tcpClient.isConnected() && deltaTime % 13 == 0)
		{
			
			tcpClient.send("1");

			int i = 0;
			while(i < 8){
				if(tcpClient.isConnected()) {
					string first = tcpClient.receive();

					if (first.length() > 0) {
						if(first.compare("none")){
							cout << first << endl;
							poem[i] = first;
						} else {
							break;
						}

						i++;
					}
				} else {
					connected = false;
					break;
				}
			}	
		} 

	} else {
		
		deltaTime = ofGetElapsedTimeMillis() - connectTime;

		if( deltaTime > 5000 )
		{
			connected = tcpClient.setup("127.0.0.1", 12345);
			connectTime = ofGetElapsedTimeMillis();

			tcpClient.send("1");

			tcpClient_opt.setup("127.0.0.1", 12345);
			tcpClient_opt.send("1");
		}
	}

	deltaTime = ofGetElapsedTimeMillis() - connectTime;

	for (int i = 0; i < N; ++i)
	{

		int delta = i + 1;
		int time_i = ofGetElapsedTimeMillis() - time_[i];
		if (time_[i] < 0 || ( i != 3 &&  time_i > 1201) || (i == 3 && time_i > 2500) ) {

			type = delta;
			value = new_values[delta - 1];

			time_[i] = -1;

			if ( abs(values[delta - 1] - value) > eps && tcpClient_opt.isConnected())
			{
				values[delta - 1] = value;

				tcpClient_opt.send("2");
				tcpClient_opt.send(type_bytes);
				tcpClient_opt.sendRawBytes(value_bytes, 4);
				tcpClient_opt.send("\n");
				
				recv_option = tcpClient_opt.receive();

				while(recv_option.length() < 1)
				{
					if (!tcpClient_opt.isConnected()) break;

					recv_option = tcpClient_opt.receive();
				}
			}
		}
	}

	//--- sound ------------------------------------------------

	if (MODE_SOUND && !mySound.getIsPlaying())
	{
		string path = ".";
		dir.allowExt("mp3");
		dir.listDir(path);

		sound ++;
		if (sound >= dir.numFiles()) sound = 0;

		mySound.loadSound(dir.getPath(sound));
		mySound.play();
		mySound.setVolume(volume);
	}

	//--- video ------------------------------------------------

	vidGrabber.update();

	cameraFbo.begin();
	ofClear(0, 0, 0, 255);
	vidGrabber.draw(0, 0);
	cameraFbo.end();

	ofPixels pix;
	cameraFbo.readToPixels(pix);
	pix.setNumChannels(3);
	ofxCvColorImage cvimg;
	cvimg.allocate(w, h);
	cvimg.setFromPixels(pix);

	fboRGBList[0].begin();
	ofClear(0, 0, 0, 255);
	cvimg.draw(0, 0);
	fboRGBList[0].end();

	for (int i = 1; i < 4; ++i)
	{
		ofxCvGrayscaleImage comp[3];
		for (int j = 0; j < 3; ++j)
		{
			comp[j].allocate(w, h);
			comp[j].set(0.0f);
		}
		
		ofxCvGrayscaleImage graycvimg;
		graycvimg.allocate(w, h);

		cvimg.convertToGrayscalePlanarImage(graycvimg, i - 1);

		comp[i - 1] = graycvimg;

		ofxCvColorImage colorComp;
		colorComp.allocate(w, h);
		colorComp.setFromGrayscalePlanarImages(comp[0], comp[1], comp[2]);

		fboRGBList[i].begin();
		ofClear(0, 0, 255, 255);
		colorComp.draw(0, 0);
		fboRGBList[i].end();
	}

	cvimg.convertRgbToHsv();

	fboHSVList[0].begin();
	ofClear(0, 0, 0, 255);
	cvimg.draw(0, 0);
	fboHSVList[0].end();

	for (int i = 1; i < 4; ++i)
	{
		ofxCvGrayscaleImage comp[3];
		for (int j = 0; j < 3; ++j)
		{
			comp[j].allocate(w, h);
			comp[j].set(0.0f);
		}
		
		ofxCvGrayscaleImage graycvimg;
		graycvimg.allocate(w, h);

		cvimg.convertToGrayscalePlanarImage(graycvimg, i - 1);
		graycvimg.convertToRange(0, 255);

		comp[i - 1] = graycvimg;

		ofxCvColorImage colorComp;
		colorComp.allocate(w, h);
		colorComp.setFromGrayscalePlanarImages(comp[0], comp[1], comp[2]);

		fboHSVList[i].begin();
		ofClear(0, 0, 255, 255);
		colorComp.draw(0, 0);
		fboHSVList[i].end();
	}

	for (int i = 0; i < N; ++i)
	{
		fboList[i].begin();
		ofClear(0, 0, 0, 255);

		if (toggles[i])
		{
			shader.begin();
			shader.setUniform1f("min_a", (float)slider[i]);
			shader.setUniform1f("min_b", (float)slider[i + 4]);
			shader.setUniform1f("min_c", (float)slider[i + 8]);
			shader.setUniform1f("max_a", (float)slider[i + 12]);
			shader.setUniform1f("max_b", (float)slider[i + 16]);
			shader.setUniform1f("max_c", (float)slider[i + 20]);
			cvimg.draw(0, 0);
			shader.end();
		}
		else
		{
			shader.begin();
			shader.setUniform1f("min_a", (float)slider[i]);
			shader.setUniform1f("min_b", (float)slider[i + 4]);
			shader.setUniform1f("min_c", (float)slider[i + 8]);
			shader.setUniform1f("max_a", (float)slider[i + 12]);
			shader.setUniform1f("max_b", (float)slider[i + 16]);
			shader.setUniform1f("max_c", (float)slider[i + 20]);
			vidGrabber.draw(0, 0);
			shader.end();
		}
		
		fboList[i].end();

		ofPixels ofpix;
		fboList[i].readToPixels(ofpix);
		ofpix.setNumChannels(3);
		ofxCvColorImage ofcvimg;
		ofcvimg.allocate(w, h);
		ofcvimg.setFromPixels(ofpix);
		
		ofcvimg.erode();
		ofcvimg.erode();
		ofcvimg.dilate();
		ofcvimg.dilate();

		ofxCvGrayscaleImage grayimg;
		grayimg.allocate(w, h);
		ofcvimg.convertToGrayscalePlanarImage(grayimg, 0);

		contourFinder.findContours(grayimg, int(5*5), int(w*h), 1, false, true);

		float max_area = 0;
		int max_j = -1;
		for(int j = 0; j < contourFinder.nBlobs; ++j)
		{
			float area = contourFinder.blobs[j].area;
			if(area > max_area)
			{
				max_area = area;
				max_j = j;
			}
		}

		if(max_j > -1)
		{
			ofcvimg.drawBlobIntoMe(contourFinder.blobs[max_j], 128);

			blobOptions[i][0] = contourFinder.blobs[max_j].centroid.x;
			blobOptions[i][1] = contourFinder.blobs[max_j].centroid.y;

			new_values[i] = smth_interpolation(blobOptions[i][0], blobOptions[i][1]);

			if(time_[i] < 0) {
				time_[i] = ofGetElapsedTimeMillis();
			}

			ofPixels campix;
			cameraFbo.readToPixels(campix);
			campix.setNumChannels(3);
			cameraimg.setFromPixels(campix);

			int color[3] = {20, 20, 20};
			string name;

			if (i == 0)
			{
				color[2] = 240;
				name = "CATEGORY";
			}

			if (i == 1)
			{
				color[1] = 240;
				name = "TITLE";
			}

			if (i == 2)
			{
				color[0] = 230;
				color[1] = 230;
				name = "PART";
			}

			if (i == 3)
			{
				color[0] = 240;
				name = "FORM";
			}

			cameraFbo.begin();
			ofClear(0, 0, 0, 255);
			cameraimg.draw(0, 0);
			
			ofSetColor(255, 255, 255);
			ofSetLineWidth(6.0);

			ofLine(blobOptions[i][0] - 10, blobOptions[i][1], blobOptions[i][0] + 10, blobOptions[i][1]);
			ofLine(blobOptions[i][0], blobOptions[i][1] - 10, blobOptions[i][0], blobOptions[i][1] + 10);

			ofSetColor(color[0], color[1], color[2]);
			ofSetLineWidth(4.0);

			ofLine(blobOptions[i][0] - 8, blobOptions[i][1], blobOptions[i][0] + 8, blobOptions[i][1]);
			ofLine(blobOptions[i][0], blobOptions[i][1] - 8, blobOptions[i][0], blobOptions[i][1] + 8);

			ofDrawBitmapStringHighlight(name, blobOptions[i][0], blobOptions[i][1] - 8);

			ofSetColor(255, 255, 255);
			cameraFbo.end();
		}

		fboList[i].begin();
		ofClear(0, 0, 0, 255);
		ofcvimg.draw(0, 0);
		fboList[i].end();
	}
}

//--------------------------------------------------------------
void ofApp::draw(){

	if (!MODE)
	{
		ofColor c1, c2;
		
		c1.set(30, 30, 30);
		c2.set(50, 30, 50);

		ofBackgroundGradient(c1, c2, OF_GRADIENT_LINEAR);

		ofSetColor(255, 255, 255);

		cameraFbo.draw(1400, 670);

		if (poem[0].compare(""))
		{
			ofSetColor(20, 20, 20);

			ofRect(120, 120, ofGetWidth() - 240, 280);

			ofSetColor(255, 255, 255);
			optFont.drawString("#СТИХОГЕНЕРАТОР", 1350, 80);

			ofSetColor(40, 40, 250);
			optFont.drawString("[Категория]> " + poem[0], 150, 180);
			ofSetColor(10, 200, 100);
			optFont.drawString("[Название]> " + poem[1], 150, 240);
			ofSetColor(200, 200, 40);
			optFont.drawString("[Часть]> № " + poem[2], 150, 300);
			ofSetColor(200, 40, 40);
			optFont.drawString("[Форма]> <" + poem[3] + ">", 150, 360);

			ofSetColor(255, 255, 255);
			poemFont.drawString(poem[4], 150, 470);
			poemFont.drawString(poem[5], 150, 550);
			poemFont.drawString(poem[6], 150, 630);
			poemFont.drawString(poem[7], 150, 710);
		}

		ofSetColor(0, 180, 60);

		if (recv_option.compare(""))
		{
			newFont.drawString("*** " + recv_option + " ***", 120, 860);
		}

		ofSetColor(255, 255, 255);

		if (mySound.getIsPlaying())
		{
			smallFont.drawString("Music: " + dir.getPath(sound), 100, 950);
		}
	}

	if(MODE == 1)
	{
		ofSetColor(40, 50, 60);

		ofRect(0, 370, ofGetWidth(), ofGetHeight());

		ofSetColor(255, 255, 255);

		for (int i = 0; i < 4; ++i)
		{
			if (toggle_MODE_COLOR)
				fboHSVList[i].draw(80 + 440 * i, 10);
			else
				fboRGBList[i].draw(80 + 440 * i, 10);
		}

		if (toggle_MODE_COLOR)
		{
			ofDrawBitmapStringHighlight("Hue", 560, 350);
			ofDrawBitmapStringHighlight("Saturation", 1000, 350);
			ofDrawBitmapStringHighlight("Value", 1440, 350);
		}
		else
		{
			ofDrawBitmapStringHighlight("Red", 560, 350);
			ofDrawBitmapStringHighlight("Green", 1000, 350);
			ofDrawBitmapStringHighlight("Blue", 1440, 350);
		}

		for (int i = 0; i < N; ++i)
		{
			fboList[i].draw(80 + 440 * i, 400);

			ofDrawBitmapStringHighlight(
					"Position: (" + ofToString(blobOptions[i][0]) + ", " + 
					ofToString(blobOptions[i][1]) + ")", 
					80 + 440 * i, 920
				);
			ofDrawBitmapStringHighlight("Value: (" + ofToString(new_values[i]) + ")", 80 + 440 * i, 940);
		}

		for (int i = 0; i < 4; ++i)
		{
			gui[i].draw();
		}

		gui_0.draw();

		ofDrawBitmapStringHighlight("'s' - close/open settings", 90, 40);
	}
}

//--------------------------------------------------------------
void ofApp::keyPressed(int key){

}

//--------------------------------------------------------------
void ofApp::keyReleased(int key){

	if (key == 's')
	{
		if (MODE == 0) { MODE = 1; }
		else if (MODE == 1) { 
			MODE = 0; 
			gui[0].saveToFile("set0.xml");
			gui[1].saveToFile("set1.xml");
			gui[2].saveToFile("set2.xml");
			gui[3].saveToFile("set3.xml");
		}
	}
	else if (key == 'l')
	{
		gui[0].loadFromFile("set0.xml");
		gui[1].loadFromFile("set1.xml");
		gui[2].loadFromFile("set2.xml");
		gui[3].loadFromFile("set3.xml");
	}
	else if (key == 'm')
	{
		if (mySound.getIsPlaying())
		{
			MODE_SOUND = 0;
			mySound.stop();
		}
		else 
		{
			mySound.play();
			MODE_SOUND = 1;
		}
	}
	else if (key == OF_KEY_UP)
	{
		volume += 0.1f;
		mySound.setVolume(volume);
	}
	else if (key == OF_KEY_DOWN)
	{
		volume -= 0.1f;
		mySound.setVolume(volume);
	}
	else if (key == OF_KEY_RIGHT)
	{
		sound ++;
		if (sound >= dir.numFiles()) sound = 0;

		mySound.loadSound(dir.getPath(sound));
		mySound.play();
		mySound.setVolume(volume);
	}
	else if (key == OF_KEY_LEFT)
	{
		sound --;
		if (sound < 0) sound = dir.numFiles() - 1;

		mySound.loadSound(dir.getPath(sound));
		mySound.play();
		mySound.setVolume(volume);
	}
}

//--------------------------------------------------------------
void ofApp::mouseMoved(int x, int y ){

}

//--------------------------------------------------------------
void ofApp::mouseDragged(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mousePressed(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mouseReleased(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::windowResized(int w, int h){

}

//--------------------------------------------------------------
void ofApp::gotMessage(ofMessage msg){

}

//--------------------------------------------------------------
void ofApp::dragEvent(ofDragInfo dragInfo){ 

}
//--------------------------------------------------------------
float ofApp::smth_interpolation(int x, int y){
	float w_step = w / 6;
	float h_step = h / 5;

	float res = (x / w_step + 6 * y / h_step) / 30 * 1.5 - 0.25;

	if (res < 0 ) res = 0.0f;
	if (res > 1 ) res = 1.0f;

	return res;
}
