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

/**
       \brief
       @author authorname
*/



#ifndef SPECIFICWORKER_H
#define SPECIFICWORKER_H

#include <genericworker.h>
#include <innermodel/innermodel.h>
#include <chrono>
#ifdef USE_QTGUI
	#include <osgviewer/osgview.h>
	#include <innermodel/innermodelviewer.h>
#endif

using namespace std::chrono;

#define MAX_HISTORY 5
#define MAX_TIMEOUT 500
#define ANATOMIC_MIN_DISTANCE 100

struct TimedApril
{
	std::chrono::time_point<std::chrono::steady_clock> timestamp;
	RoboCompAprilTags::tag tag;
};

class SpecificWorker : public GenericWorker
{
Q_OBJECT

//	QTimer apriltag_timeout;
	std::shared_ptr<InnerModel> innerModel;
	QHash<int, QQueue<TimedApril> > seen_tags;
	std::map<int, RoboCompHandDetection::Hand> hands;
	QMap<int, RoboCompAprilTags::tag > april_averages;
	QMap<int, int> hands_history;
	QMap<int, int> hand_to_april_id;
	mutable std::mutex mutex_inner;
	typedef std::lock_guard<std::mutex> guard;


public:
	SpecificWorker(MapPrx& mprx);
	~SpecificWorker();
	bool setParams(RoboCompCommonBehavior::ParameterList params);

	void AprilTags_newAprilTagAndPose(const tagsList &tags, const RoboCompGenericBase::TBaseState &bState, const RoboCompJointMotor::MotorStateMap &hState);
	void AprilTags_newAprilTag(const tagsList &tags);
	void TouchPoints_detectedTouchPoints(const TouchPointsSeq &touchpoints);


public slots:
	void compute();
	void initialize(int period);
//	void remove_old_apritag();

private:
	void get_apriltag_average();
	void delete_apriltag(int id);
	void update_hands(RoboCompHandDetection::Hands hands);
	float euclidean3D_distance(float x1, float y1, float z1, float x2, float y2, float z2);
	RoboCompIntegratedHand::Hand fill_integrated_hand(RoboCompHandDetection::Hand hand, int id);

//	InnerModel *innerModel;

#ifdef USE_QTGUI
	OsgView *osgView;
	InnerModelViewer *innerModelViewer;
#endif

};

#endif
