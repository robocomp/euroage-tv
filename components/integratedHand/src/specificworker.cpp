/*
 *    Copyright (C)2019 by YOUR NAME HERE
 *
 *    This file is part of RoboComp
 *
 *    RoboComp is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    RoboComp is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
 */
#include "specificworker.h"

/**
* \brief Default constructor
*/
SpecificWorker::SpecificWorker(MapPrx& mprx) : GenericWorker(mprx)
{

#ifdef USE_QTGUI
	innerModelViewer = NULL;
	osgView = new OsgView(this);
	this->setMinimumSize(800,800);
	osgView->setMinimumSize(800,800);
	osgView->getCamera()->setViewport(new osg::Viewport(0, 0, 800, 800));
//	osgView->setUpViewInWindow(50,50,800,800);
	osgGA::TrackballManipulator *tb = new osgGA::TrackballManipulator;
	// The place where the camera will have its home position
	osg::Vec3d eye(osg::Vec3(-1100,900., 0000.));
	// The point where the camera will look at
	osg::Vec3d center(osg::Vec3(0.,400.,-0.));
	// Define where the camera have it up/top position
	osg::Vec3d up(osg::Vec3(0.,1.,0.));
	// Set the Home / Default /Intial position of the camera. It's also the position where it goes when you use the spacebar
	tb->setHomePosition(eye, center, up, false);
//	tb->setByMatrix(osg::Matrixf::lookAt(eye,center,up));
	osgView->setCameraManipulator(tb);
#endif
}

/**
* \brief Default destructor
*/
SpecificWorker::~SpecificWorker()
{
	std::cout << "Destroying SpecificWorker" << std::endl;
}

bool SpecificWorker::setParams(RoboCompCommonBehavior::ParameterList params)
{
//       THE FOLLOWING IS JUST AN EXAMPLE
//	To use innerModelPath parameter you should uncomment specificmonitor.cpp readConfig method content
	try
	{
		RoboCompCommonBehavior::Parameter par = params.at("InnerModelPath");
		std::string innermodel_path = par.value;
		innerModel = std::make_shared<InnerModel>(innermodel_path);
//		innerModel = new InnerModel(innermodel_path);
	}
	catch(std::exception e) { qFatal("Error reading config params"); }
#ifdef USE_QTGUI
	innerModelViewer = new InnerModelViewer (innerModel, "world", osgView->getRootGroup(), true);
#endif

	return true;
}

void SpecificWorker::initialize(int period)
{
	std::cout << "Initialize worker" << std::endl;
	this->Period = period;
	timer.start(Period);
	TRoi search_roi_class;
	search_roi_class.y = 480 / 2 - 100;
	search_roi_class.x = 640 / 2 - 100;
	search_roi_class.w = 200;
	search_roi_class.h = 200;
//	search_roi = (
//			search_roi_class.x, search_roi_class.y, search_roi_class.h, search_roi_class.w);
	handdetection_proxy->addNewHand(1,search_roi_class);
}

void SpecificWorker::compute()
{
	QMutexLocker locker(mutex);
 	try {
 		auto handCount = handdetection_proxy->getHandsCount();
 		if(handCount > 0)
		{
			 auto hands = handdetection_proxy->getHands();
			 std::cout<<"Detected Hands:"<< handCount <<" Coordinates: "<<hands[0].centerMass[0]<<", "<<hands[0].centerMass[1]<<", "<<hands[0].centerMass[2]<<endl;
			 innerModel->updateTransformValues("hand_t", -1*hands[0].centerMass[1],-hands[0].centerMass[2], -1*hands[0].centerMass[0], 0,0,0);
			 innerModel->save("patatita.xml");
		}
		else
		{
			std::cout<<"Waiting for hands"<<endl;
 		}

	}
 	catch(const Ice::Exception &e)
 	{
 		std::cout << "Error reading from Camera" << e << std::endl;
 	}

#ifdef USE_QTGUI
	if (innerModelViewer) innerModelViewer->update();
	osgView->frame();
#endif
//	milliseconds ms = duration_cast< milliseconds >(
//			system_clock::now().time_since_epoch()
//	);
// 	std::cout<<ms.count()<<endl;

//	innerModel->save(QString("mejillon.xml"));
}


void SpecificWorker::TouchPoints_detectedTouchPoints(const TouchPointsSeq &touchpoints)
{
	std::cout << "TouchPoint detected" << std::endl;
}


