//******************************************************************
// 
//  Generated by RoboCompDSL
//  
//  File name: IDSLs/AdminGameInterface.ice
//  Source: IDSLs/AdminGameInterface.idsl
//  
//****************************************************************** 
#ifndef EUROAGEGAMES_ICE
#define EUROAGEGAMES_ICE
module EuroAgeGames
{
	enum StatusType { waiting, playing, paused, continued, finished };
	struct Status
	{
		 StatusType currentStatus;
		 string date;
	};
	struct Metrics
	{
		 float distance;
		 int num_hand_open;
		 int num_hand_closed;
		 int num_screen_touched;
		 int num_helps;
		 int num_hits;
		 int num_fails;
		 float idle_time;
	};
	sequence <string> list_players;
	interface AdminGame
	{
		void admin_start (list_players players, string game);
		void admin_stop ();
		void admin_pause ();
		void admin_continue ();
		void admin_reset ();
	};
	interface GameMetrics
	{
		Metrics metrics_obtained ();
		Status status_changed ();
	};
};

#endif