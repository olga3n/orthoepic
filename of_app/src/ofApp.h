#pragma once

#include "ofMain.h"
#include "ofxNetwork.h"
#include "ofxTrueTypeFontUC.h"
#include "ofxOpenCv.h"
#include "ofxGui.h"

class ofApp : public ofBaseApp{

	public:
		void setup();
		void update();
		void draw();

		void keyPressed(int key);
		void keyReleased(int key);
		void mouseMoved(int x, int y );
		void mouseDragged(int x, int y, int button);
		void mousePressed(int x, int y, int button);
		void mouseReleased(int x, int y, int button);
		void windowResized(int w, int h);
		void dragEvent(ofDragInfo dragInfo);
		void gotMessage(ofMessage msg);

		float smth_interpolation(int x, int y);

		//--- network ----------------------------------------------

		ofxTCPClient tcpClient;
		ofxTCPClient tcpClient_opt;
		
		bool connected;
		int connectTime;
		int deltaTime;

		//--- data -------------------------------------------------

		string recv_option;
		string poem[8];

		char type;
		float value;

		float *values;
		float *new_values;

		float eps;
		int *time_;

		//--- sound ------------------------------------------------

		ofDirectory dir;
		ofSoundPlayer mySound;
		int sound;
		float volume;

		//--- video ------------------------------------------------

		ofVideoGrabber vidGrabber;

		float w;
		float h;

		int N;
		ofFbo *fboList;
		ofFbo *fboHSVList;
		ofFbo *fboRGBList;
		int **blobOptions;

		ofxCvContourFinder contourFinder;
		ofShader shader;

		ofFbo cameraFbo;
		ofxCvColorImage cameraimg;

		//--- interface --------------------------------------------

		ofxTrueTypeFontUC poemFont;
		ofxTrueTypeFontUC optFont;
		ofxTrueTypeFontUC newFont;
		ofxTrueTypeFontUC smallFont;

		int MODE;
		int MODE_SOUND;

		ofxPanel gui[4];
		ofxSlider<int> slider[24];

		ofxPanel gui_0;
		ofxToggle toggle_MODE_COLOR;

		ofxToggle toggles[4];
};
