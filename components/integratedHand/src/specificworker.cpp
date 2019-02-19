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
//	TRoi search_roi_class;
//	search_roi_class.y = 480 / 2 - 100;
//	search_roi_class.x = 640 / 2 - 100;
//	search_roi_class.w = 200;
//	search_roi_class.h = 200;
//	search_roi = (
//			search_roi_class.x, search_roi_class.y, search_roi_class.h, search_roi_class.w);
	//handdetection_proxy->addNewHand(1,search_roi_class);
}

void SpecificWorker::compute()
{
	QMutexLocker locker(mutex);
 	try {
 		auto handCount = handdetection_proxy->getHandsCount();
 		if(handCount > 0)
		{
			 auto hands = handdetection_proxy->getHands();
			try {
				std::cout<<"Detected Hands:"<< handCount <<" Coordinates: "<<hands[0].centerMass3D[0]<<", "<<hands[0].centerMass3D[1]<<", "<<hands[0].centerMass3D[2]<<endl;
				innerModel->updateTransformValues("hand_t", -hands[0].centerMass3D[1],-hands[0].centerMass3D[2], -hands[0].centerMass3D[0], 0,0,0);
			}
			catch(...)
			{
				std::cout<<"Problem updating transform"<<endl;
			}

		}
		else
		{
			std::cout<<"Waiting for hands"<<endl;
 		}

	}
 	catch(const Ice::Exception &e)
 	{
 		std::cout << "Error reading from HandDetection" << e << std::endl;
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


void SpecificWorker::AprilTags_newAprilTagAndPose(const tagsList &tags, const RoboCompGenericBase::TBaseState &bState, const RoboCompJointMotor::MotorStateMap &hState)
{
//	std::cout<<"AprilTags_newAprilTagAndPose"<<std::endl;
}

void SpecificWorker::AprilTags_newAprilTag(const tagsList &tags)
{

	for(int i = 0; i< tags.size(); i++)
	{
		map<int, RoboCompAprilTags::tag>::const_iterator it = seen_tags.find(tags[i].id);
		if(it!=seen_tags.end())
		{
			std::cout<<"Moving tag ("<<tags[i].id<<") "<<tags[i].ty<<", "<<-tags[i].tz<<", "<<-tags[i].tx<<endl;
//			innerModel->updateTransformValues("tag_t_"+QString::number(tags[i].id), tags[i].ty, -tags[i].tz, -tags[i].tx, 0,0,0);
		}
		else
		{
			std::cout<<"New tag ("<<tags[i].id<<") "<<tags[i].ty<<", "<<-tags[i].tz<<", "<<-tags[i].tx<<endl;
			seen_tags.insert(std::make_pair(tags[i].id, tags[i]));
//			auto new_tag_transform = innerModel->newTransform(QString::number(tags[i].id), "static", innerModel->getNode("t_tcamera"), tags[i].ty, -tags[i].tz, -tags[i].tx, 0, 0, 0);
			InnerModelNode *camera_transform;
			camera_transform = innerModel->getNode("t_tcamera");
			InnerModelTransform *new_tag_transform;
			new_tag_transform = innerModel->newTransform("tag_t_"+QString::number(tags[i].id), "static", camera_transform, 0, 0, 0, 0, 0, 0);
			camera_transform->addChild(new_tag_transform);
			InnerModelPlane *new_plane;
			new_plane = innerModel->newPlane("tag_p_"+QString::number(tags[i].id), new_tag_transform, "#7FFFD4", 500, 100, 500, 1000,  0,1,0,   0,0,0,  false);
			new_tag_transform->addChild(new_plane);
			innerModel->update();
			innerModel->save("saved_inner.xml");

		}
//		std::cout<<"Id : "<<tags[i].id<<std::endl;
//		if(tags[i].id==0)
//		{
//			std::cout<<"Position : "<<tags[i].tx<<", "<<tags[i].ty<<", "<<tags[i].tz<<std::endl;
//			innerModel->updateTransformValues(, tags[i].ty, -tags[i].tz, -tags[i].tx, 0,0,0);
//		}
	}
}

void SpecificWorker::TouchPoints_detectedTouchPoints(const TouchPointsSeq &touchpoints)
{
	std::cout << "TouchPoint detected" << std::endl;
}


