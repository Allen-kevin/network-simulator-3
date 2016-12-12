/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

/**
 * Author: Brett Levasseur
 *
 * This file runs a simple simulation of TCP CUBIC. This file was made based
 * on another example simulation, hence the original copyright at the top
 * of this file.
 */

#include <fstream>
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

#include "ns3/flow-monitor.h"
#include "ns3/flow-monitor-helper.h"

#include <iostream>
#include <string>

using namespace std;

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("WestwoodTesting");

/**
 * The following section of comments comes from the example this simulation
 * modified. The overal network setup of two nodes and one link is still the
 * the same though the characteristics of the link may be modified to test
 * different scenarios.
 */

// ===========================================================================
//
//         node 0                 node 1
//   +----------------+    +----------------+
//   |    ns-3 TCP    |    |    ns-3 TCP    |
//   +----------------+    +----------------+
//   |    10.1.1.1    |    |    10.1.1.2    |
//   +----------------+    +----------------+
//   | point-to-point |    | point-to-point |
//   +----------------+    +----------------+
//           |                     |
//           +---------------------+
//                5 Mbps, 2 ms
//
//
// We want to look at changes in the ns-3 TCP congestion window.  We need
// to crank up a flow and hook the CongestionWindow attribute on the socket
// of the sender.  Normally one would use an on-off application to generate a
// flow, but this has a couple of problems.  First, the socket of the on-off 
// application is not created until Application Start time, so we wouldn't be 
// able to hook the socket (now) at configuration time.  Second, even if we 
// could arrange a call after start time, the socket is not public so we 
// couldn't get at it.
//
// So, we can cook up a simple version of the on-off application that does what
// we want.  On the plus side we don't need all of the complexity of the on-off
// application.  On the minus side, we don't have a helper, so we have to get
// a little more involved in the details, but this is trivial.
//
// So first, we create a socket and do the trace connect on it; then we pass 
// this socket into the constructor of our simple application which we then 
// install in the source node.
// ===========================================================================
//

/**
 * MyApp
 * A custom application used by a few of the examples in ns-3. This code
 * defines an application to run during the simulation that setups connections
 * and manages sending data.
 */
class MyApp : public Application 
{
public:

  /**
   * Default constructors.
   */
  MyApp ();
  virtual ~MyApp();

  /**
   * Setup the example application.
   */
  void Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate);
  void ChangeBw (void); //wanwenkai
  void ScheduleBw (void); //wanwenkai
  //string m_bandwidth; //wanwenkai

private:
  virtual void StartApplication (void);
  virtual void StopApplication (void);

  void ScheduleTx (void);
  void SendPacket (void);

  Ptr<Socket>     m_socket;
  Address         m_peer;
  uint32_t        m_packetSize;
  uint32_t        m_nPackets;
  DataRate        m_dataRate;
  EventId         m_sendEvent;
  bool            m_running;
  uint32_t        m_packetsSent;
  string   	      m_bandwidth; //wanwenkai       
  uint32_t	      m_timer_value; //wanwenkai

};

/**
 * Default constructor.
 */
MyApp::MyApp ()
  : m_socket (0), 
    m_peer (), 
    m_packetSize (0), 
    m_nPackets (0), 
    m_dataRate (0), 
    m_sendEvent (), 
    m_running (false), 
    m_packetsSent (0),
	m_bandwidth ("7.2Mbps"), //wanwenkai
	m_timer_value (200) //wanwenkai
{
}

/**
 * Default deconstructor.
 */
MyApp::~MyApp()
{
  m_socket = 0;
}

/**
 * Setup the application.
 * Parameters:
 * socket     Socket to send data to.
 * address    Address to send data to.
 * packetSize Size of the packets to send.
 * nPackets   Number of packets to send.
 * dataRate   Data rate used to determine when to send the packets.
 */
void
MyApp::Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate)
{
  m_socket = socket;
  m_peer = address;
  m_packetSize = packetSize;
  m_nPackets = nPackets;
  m_dataRate = dataRate;
}

/**
 * Start sending data to the address given in the Setup method.
 */
void
MyApp::StartApplication (void)
{
  m_running = true;
  m_packetsSent = 0;
  m_socket->Bind ();
  m_socket->Connect (m_peer);
  SendPacket ();
  //ChangeBw ();
}

/**
 * Stop sending data to the address given in the Setup method.
 */
void 
MyApp::StopApplication (void)
{
  m_running = false;
  //myfile.close();
  if (m_sendEvent.IsRunning ())
    {
      Simulator::Cancel (m_sendEvent);
    }

  if (m_socket)
    {
      m_socket->Close ();
    }
}

/**
 * Send a packet to the receiver.
 */
void 
MyApp::SendPacket (void)
{
  Ptr<Packet> packet = Create<Packet> (m_packetSize);
  m_socket->Send (packet);

  if (++m_packetsSent < m_nPackets)
    {
      ScheduleTx ();
    }
  else
    {
      std::cout << "Done sending packets: " << m_packetsSent;
    }
}

/**
 * Schedule when the next packet will be sent.
 */
void 
MyApp::ScheduleTx (void)
{
  if (m_running)
    {
      Time tNext (Seconds (m_packetSize * 8 / static_cast<double> (m_dataRate.GetBitRate ())));
      NS_LOG_INFO("Send next packet at: " << tNext);
      m_sendEvent = Simulator::Schedule (tNext, &MyApp::SendPacket, this);
    }
}

/* wanwenkai*/
/*ifstream bwfile("downlink.txt");
//bwfile.open ("downlink.txt", ios::in | ios::app);
//string m_bandwidth = "7.2Mb"; //wanwenkai
PointToPointHelper pointToPoint;

void
MyApp::ChangeBw (void)
{

	getline(bwfile,m_bandwidth);
//	cout << "m_bandwidth = "<< m_bandwidth << endl;
    pointToPoint.SetDeviceAttribute ("DataRate", StringValue (m_bandwidth));

	if (!bwfile.eof())
	{
		ScheduleBw ();
	}
	else
	{
		std::cout << "end of file!" << endl;
	}

}

void
MyApp::ScheduleBw (void)
{
	Simulator::Schedule (MilliSeconds (m_timer_value), &MyApp::ChangeBw, this);
}
 end */

/* Detect if the output is to a new file that needs a header or not. */
bool newFile = true;

/**
 * Callback method to log changes to the congestion window.
 */
static void
CwndChange (uint32_t oldCwnd, uint32_t newCwnd)
{
  NS_LOG_UNCOND (Simulator::Now ().GetSeconds () << "\t" << newCwnd);

  // Write to a file
  ofstream myfile;
  if (newFile)
    {
      myfile.open ("cwnd.log");
      newFile = false;
    }
  else
    {
       myfile.open ("cwnd.log", ios::out | ios::app);
    }
     myfile << Simulator::Now ().GetSeconds () << " " << newCwnd << "\n"; 
     myfile.close();

}

/* wanwenkai */
/**
 * Callback method to log changes to the slow start threshold.
 */
static void
SsthreshChange (uint32_t oldSsthresh, uint32_t newSsthresh)
{
  NS_LOG_UNCOND (Simulator::Now ().GetSeconds () << "\t" << newSsthresh);

  // Write to a file
  ofstream myfile;
  if (newFile)
    {
      myfile.open ("ssthresh.log");
      newFile = false;
    }
  else
    {
       myfile.open ("ssthresh.log", ios::out | ios::app);
    }
     myfile << Simulator::Now ().GetSeconds () << " " << newSsthresh << "\n"; 
     myfile.close();

}
/**
 * Callback method to log changes to the round trip time.
 */
static void
RttChange (Time oldRtt, Time newRtt)
{
  NS_LOG_UNCOND (Simulator::Now ().GetSeconds () << "\t" << newRtt);

  // Write to a file
  ofstream myfile;
  if (newFile)
    {
      myfile.open ("rtt.log");
      newFile = false;
    }
  else
    {
       myfile.open ("rtt.log", ios::out | ios::app);
    }
     myfile << Simulator::Now ().GetSeconds () << " " << newRtt << "\n"; 
     myfile.close();

}
/* end */
/**
 * Log packet drops.
 */
static void
RxDrop (Ptr<const Packet> p)
{
  NS_LOG_UNCOND ("RxDrop at " << Simulator::Now ().GetSeconds ());
}


/**
 * Main method that creates, configures and runs the simulation.
 */
int 
main (int argc, char *argv[])
{
  // Set the TCP variant to use.
  Config::SetDefault ("ns3::TcpL4Protocol::SocketType", TypeIdValue (TcpWestwood::GetTypeId())); 
  Config::SetDefault ("ns3::TcpSocket::SegmentSize",  UintegerValue(1000));

  LogComponentEnable( "TcpWestwood", LOG_LEVEL_INFO);


  // Create the nodes in the network.
  NodeContainer nodes;
  nodes.Create (2);

  Ptr<MyApp> app = CreateObject<MyApp> ();

  // Setup the connection between the nodes.
  PointToPointHelper pointToPoint;
  //app->ChangeBw (); //wanwenkai
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("7.2Mbps"));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("150ms"));
  pointToPoint.SetDeviceAttribute ("Mtu", UintegerValue (1500));


  // Add nodes to NetDeviceContainer.
  NetDeviceContainer devices;
  devices = pointToPoint.Install (nodes);

  
  // Set the error rate for the reciever.
  Ptr<RateErrorModel> em = CreateObject<RateErrorModel> ();
  em->SetAttribute ("ErrorRate", DoubleValue (0.000002));
  devices.Get (1)->SetAttribute ("ReceiveErrorModel", PointerValue (em));


  // Set the Internet for the devices including adressing.
  InternetStackHelper stack;
  stack.Install (nodes);
  Ipv4AddressHelper address;
  address.SetBase ("10.1.1.0", "255.255.255.252");
  Ipv4InterfaceContainer interfaces = address.Assign (devices);


  // Set the address of the sink or receiver.
  uint16_t sinkPort = 8080;
  Address sinkAddress (InetSocketAddress (interfaces.GetAddress (1), sinkPort));
  PacketSinkHelper packetSinkHelper ("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), sinkPort));

  // Set an application on the sink to receive the data and return the expected TCP ACKs.
  ApplicationContainer sinkApps = packetSinkHelper.Install (nodes.Get (1));
  sinkApps.Start (Seconds (0.1));
  sinkApps.Stop (Seconds (61.0));


  // Set the TCP congestion control algorithm to use.
  TypeId tid = TypeId::LookupByName ("ns3::TcpWestwood");
  Config::Set ("/NodeList/*/$ns3::TcpL4Protocol/SocketType", TypeIdValue (tid));
  Ptr<Socket> ns3TcpSocket = Socket::CreateSocket (nodes.Get (0), /*tid*/ TcpSocketFactory::GetTypeId ());

  // Trace changes to the congestion window.
  ns3TcpSocket->TraceConnectWithoutContext ("CongestionWindowWestwood", MakeCallback (&CwndChange));
/* wanwenkai */
  ns3TcpSocket->TraceConnectWithoutContext ("SlowStartThresholdWestwood", MakeCallback (&SsthreshChange));
  ns3TcpSocket->TraceConnectWithoutContext ("RoundTripTimeWestwood", MakeCallback (&RttChange));
/* end */
  // Set the application on the sender with the size of the packets, number of
  // packets to send and the rate to send them at.
  // Ptr<MyApp> app = CreateObject<MyApp> ();
  app->Setup (ns3TcpSocket, sinkAddress, 1000, 100000000, DataRate ("1Mbps"));
  nodes.Get (0)->AddApplication (app);
  app->SetStartTime (Seconds (0.2));
  app->SetStopTime (Seconds (60.0));
  
  // Trace packet drops.
  devices.Get (1)->TraceConnectWithoutContext ("PhyRxDrop", MakeCallback (&RxDrop));


  // Run the simulation
  Simulator::Stop (Seconds (62.0));

  FlowMonitorHelper flowmon;
  Ptr<FlowMonitor> monitor = flowmon.Install( nodes );

  Simulator::Run ();

  monitor->SerializeToXmlFile ("results.xml", true, true);

  std::cout << "Simulation done, time " << Simulator::Now().GetSeconds () << " seconds \n";

  // Clean up.
  Simulator::Destroy ();
  return 0;
}

