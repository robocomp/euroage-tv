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
	osg::Vec3d eye(osg::Vec3(-1500,700., 100.));
	// The point where the camera will look at
	osg::Vec3d center(osg::Vec3(0.,600.,-0.));
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
//	connect(this->apriltag_timeout, SIGNAL(timeout()), this, SLOT(this->remove_old_apritag()));
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
	guard inner(mutex_inner);
	this->get_apriltag_average();
	QMutexLocker locker(mutex);
 	try {
 		auto hands = handdetection_proxy->getHands();
		try {

			this->update_hands(hands);

		}
		catch(...)
		{
			std::cout<<"Problem updating transform"<<endl;
		}
		int unknown_hands_count = 0;
		RoboCompIntegratedHand::Hands out_hands;
		for(auto &hand: hands)
		{
			RoboCompIntegratedHand::Hand out_hand;
			if(!this->hand_to_april_id.contains(hand.id)) {
				float min_distance = MAXFLOAT;
				int min_apriltag_id = -1;
				for (auto tag: this->april_averages) {
					auto distance = this->euclidean3D_distance(tag.ty, -tag.tz, -tag.tx, -hand.centerMass3D[1],
															   -hand.centerMass3D[2], -hand.centerMass3D[0]);
					std::cout << "Distance " << distance;
					if (distance < min_distance and distance < ANATOMIC_MIN_DISTANCE) {
						min_distance = distance;
						min_apriltag_id = tag.id;
					}
				}
				if (min_apriltag_id != -1) {
					this->hand_to_april_id[hand.id] = min_apriltag_id;
					out_hand = this->fill_integrated_hand(hand, min_apriltag_id);
				} else{
					unknown_hands_count++;
					out_hand = this->fill_integrated_hand(hand, -unknown_hands_count);
				}
			} else{
				out_hand = this->fill_integrated_hand(hand, this->hand_to_april_id[hand.id]);
			}
			out_hands.push_back(out_hand);
		}
		try {
			this->integratedhand_pubproxy->detectedHands(out_hands);
		}
		catch(const Ice::Exception &e)
		{
			std::cout << "Error publishing hand" << e << std::endl;
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

RoboCompIntegratedHand::Hand SpecificWorker::fill_integrated_hand(RoboCompHandDetection::Hand hand, int id)
{
	RoboCompIntegratedHand::Hand out_hand;
	out_hand.id = id;
	out_hand.touched = false;
	out_hand.fist = false;
	out_hand.centerMass.x = hand.centerMass3D[0];
	out_hand.centerMass.y = hand.centerMass3D[1];
	out_hand.centerMass.z = hand.centerMass3D[2];
	return out_hand;

}


float SpecificWorker::euclidean3D_distance(float x1, float y1, float z1, float x2, float y2, float z2)
{
	float xSqr = (x1 - x2) * (x1 - x2);
	float ySqr = (y1 - y2) * (y1 - y2);
	float zSqr = (z1 - z2) * (z1 - z2);

	return sqrt(xSqr + ySqr + zSqr);
}

void SpecificWorker::AprilTags_newAprilTagAndPose(const tagsList &tags, const RoboCompGenericBase::TBaseState &bState, const RoboCompJointMotor::MotorStateMap &hState)
{
//	std::cout<<"AprilTags_newAprilTagAndPose"<<std::endl;
}

void SpecificWorker::AprilTags_newAprilTag(const tagsList &tags)
{
	guard inner(mutex_inner);
	std::chrono::time_point current_time = std::chrono::steady_clock::now();
	for(auto tag: tags)
	{
		if(seen_tags.contains(tag.id))
		{
			TimedApril t;
			t.timestamp = current_time;
			t.tag = tag;
			seen_tags[tag.id].enqueue(t);
			if(seen_tags[tag.id].size()>MAX_HISTORY)
			{
				seen_tags[tag.id].dequeue();

			}
			std::cout<<"Apriltags quque size: "<<seen_tags[tag.id].size();
		}
		else
		{
			seen_tags[tag.id] = QQueue<TimedApril>();
			TimedApril t;
			t.timestamp = current_time;
			t.tag = tag;
			seen_tags[tag.id].enqueue(t);
			std::cout<<"New tag ("<<tag.id<<") "<<tag.ty<<", "<<-tag.tz<<", "<<-tag.tx<<endl;
//			auto new_tag_transform = innerModel->newTransform(QString::number(tag.id), "static", innerModel->getNode("t_tcamera"), tag.ty, -tag.tz, -tag.tx, 0, 0, 0);
			InnerModelNode *camera_transform;
			camera_transform = innerModel->getNode("t_tcamera");
			InnerModelTransform *new_tag_transform;
			new_tag_transform = innerModel->newTransform("tag_t_"+QString::number(tag.id), "static", camera_transform,  tag.ty, -tag.tz, -tag.tx, 0,0,0);
			camera_transform->addChild(new_tag_transform);
			InnerModelPlane *new_plane;
			new_plane = innerModel->newPlane("tag_p_"+QString::number(tag.id), new_tag_transform, "#7FFFD4", 10, 10, 10, 0,  0,1,0,   0,0,0,  false);
			new_tag_transform->addChild(new_plane);
			innerModelViewer->recursiveConstructor(new_tag_transform);
			innerModel->update();
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
//	for(auto &touchpoint: touchpoints)
//	{
//		IntegratedHand::Hand hand;
//		hand.touched = true;
//		hand.fist = false;
//		hand.touchPos = touchpoint.lastPos;
//		hand.centerMass.x = this->april_averages
//
//		//Look for the nearest apriltag between all
//
//		//Publish
//	}
////	struct Hand{
////		int id;
////		bool touched;
////		bool fist;
////		Pos2D touchPos;
////		Pos3D centerMass;
////	};
//
////	struct TouchPoint
////	{
////		::Ice::Int id;
////		StateEnum state;
////		KeyPoint fingertip;
////		KeyPoint lastPos;
////	};
//	std::cout << "TouchPoint detected" << std::endl;

}


void SpecificWorker::get_apriltag_average()
{
	auto current_time = std::chrono::steady_clock::now();

	for(auto id: this->seen_tags.keys())
	{
		auto &april_time_vec = this->seen_tags[id];
		this->april_averages[id].tx=0;
		this->april_averages[id].ty=0;
		this->april_averages[id].tz=0;

		for(auto &aprilt_time: april_time_vec)
		{
			auto duration = std::chrono::duration_cast<  std::chrono::milliseconds>
					(current_time - aprilt_time.timestamp);

			if(duration.count() < MAX_TIMEOUT)
			{
				this->april_averages[id].tx+=aprilt_time.tag.tx;
				this->april_averages[id].ty+=aprilt_time.tag.ty;
				this->april_averages[id].tz+=aprilt_time.tag.tz;
				//average
			}
			else {
				//TODO: It will make boom
				april_time_vec.dequeue();

			}


		}
		if(april_time_vec.size()>0)
		{
			this->april_averages[id].tx/=april_time_vec.size();
			this->april_averages[id].ty/=april_time_vec.size();
			this->april_averages[id].tz/=april_time_vec.size();
			std::cout<<"Moving tag ("<<id<<") "<<this->april_averages[id].ty<<", "<<-this->april_averages[id].tz<<", "<<-this->april_averages[id].tx<<endl;
			innerModel->updateTransformValues("tag_t_"+QString::number(id), this->april_averages[id].ty, -this->april_averages[id].tz, -this->april_averages[id].tx, 0,0,0);
		}
		else
		{
			this->delete_apriltag(id);
		}
	}

}

void SpecificWorker::delete_apriltag(int id)
{
	QString name = "tag_t_"+QString::number(id);
	std::cout<<"Removing id "<<id<<endl;
	InnerModelNode* node = innerModel->getNode(name);
	if(node!=NULL) {
		QStringList l;
		innerModelViewer->recursiveRemove(node);
		innerModel->removeSubTree(node, &l);
		innerModel->update();
		qDebug() << l;
		this->seen_tags.remove(id);
		this->april_averages.remove(id);
	}
	InnerModelNode* node3 = innerModel->getNode(name);
	if(node3 == NULL)
	{
		std::cout<<"BORRADO innermodel node";
	}
}

void SpecificWorker::update_hands(RoboCompHandDetection::Hands hands)
{

	QList<int> keys = this->hands_history.keys();
//	qDebug()<<"keys1 "<<keys;
	for(auto &hand: hands)
	{

		if(!this->hands_history.contains(hand.id))
		{
			innerModel->getNode("t_tcamera");
			InnerModelNode *camera_transform;
			this->hands_history[hand.id]=1;
			camera_transform = innerModel->getNode("t_tcamera");
			InnerModelTransform *new_hand_transform = innerModel->newTransform("hand_t_"+QString::number(hand.id), "static", camera_transform,  -hand.centerMass3D[1],-hand.centerMass3D[2], -hand.centerMass3D[0], 0,0,0);
			camera_transform->addChild(new_hand_transform);
			InnerModelPlane *new_plane = innerModel->newPlane("hand_p_"+QString::number(hand.id), new_hand_transform, "#b969db", 15, 15, 15, 0,  0,1,0,   0,0,0,  false);
			new_hand_transform->addChild(new_plane);
			innerModelViewer->recursiveConstructor(new_hand_transform);
			innerModel->update();
		}
		else {
			innerModel->updateTransformValues("hand_t_"+QString::number(hand.id), -hand.centerMass3D[1],-hand.centerMass3D[2], -hand.centerMass3D[0], 0,0,0);
			this->hands_history[hand.id]++;
			if(this->hands_history[hand.id]>MAX_HISTORY)
				this->hands_history[hand.id] = MAX_HISTORY;
		}
		keys.removeAll(hand.id);
	}
//	qDebug()<<"keys2 "<<keys;
	for(auto &key: keys)
	{
		this->hands_history[key]--;
//		qDebug()<<"Times seen "<<this->hands_history[key];
		if(this->hands_history[key]<=0)
		{
			QString name = "hand_t_"+QString::number(key);
//			std::cout<<"Removing key "<<key<<endl;
			InnerModelNode* node = innerModel->getNode(name);
			if(node!=NULL) {
				QStringList l;
				innerModelViewer->recursiveRemove(node);
				innerModel->removeSubTree(node, &l);
				innerModel->update();
				qDebug() << l;
				this->hands_history.remove(key);
			}
		}
	}
}