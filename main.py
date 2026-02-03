import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';

// --- MAIN APP START ---
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(); // Firebase සම්බන්ධ කිරීම
  runApp(CryptoSignalApp());
}

class CryptoSignalApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        primaryColor: Colors.orangeAccent,
        scaffoldBackgroundColor: Color(0xFF0D0D0D), // Premium Dark Background
      ),
      home: LoginPage(),
    );
  }
}

// --- 1. LOGIN PAGE (Admin Credentials) ---
class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _email = TextEditingController();
  final _pass = TextEditingController();

  void handleLogin() {
    if (_email.text == "ushan2008@gmail.com" && _pass.text == "2008") {
      Navigator.push(context, MaterialPageRoute(builder: (context) => AdminDashboard()));
    } else {
      Navigator.push(context, MaterialPageRoute(builder: (context) => UserDashboard()));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(30),
          child: Column(
            children: [
              Icon(Icons.bolt, size: 100, color: Colors.orangeAccent),
              Text("CRYPTO PRO SIGNALS", style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
              SizedBox(height: 40),
              TextField(controller: _email, decoration: InputDecoration(labelText: "Email", border: OutlineInputBorder())),
              SizedBox(height: 15),
              TextField(controller: _pass, obscureText: true, decoration: InputDecoration(labelText: "Password", border: OutlineInputBorder())),
              SizedBox(height: 25),
              ElevatedButton(
                onPressed: handleLogin,
                child: Text("SIGN IN"),
                style: ElevatedButton.styleFrom(minimumSize: Size(double.infinity, 55), backgroundColor: Colors.orangeAccent),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// --- 2. ADMIN DASHBOARD (Post & Pin Signals) ---
class AdminDashboard extends StatelessWidget {
  final _pair = TextEditingController();
  final _entry = TextEditingController();
  final _tp = TextEditingController();
  final _sl = TextEditingController();

  void postSignal(BuildContext context) {
    FirebaseFirestore.instance.collection('signals').add({
      'pair': _pair.text.toUpperCase(),
      'entry': _entry.text,
      'tp': _tp.text,
      'sl': _sl.text,
      'status': 'ACTIVE',
      'isPinned': false,
      'timestamp': FieldValue.serverTimestamp(),
    });
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Signal Posted Successfully!")));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Admin Control Panel")),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(controller: _pair, decoration: InputDecoration(labelText: "Pair (e.g. SOL/USDT)")),
            TextField(controller: _entry, decoration: InputDecoration(labelText: "Entry Price Range")),
            TextField(controller: _tp, decoration: InputDecoration(labelText: "Take Profit Target")),
            TextField(controller: _sl, decoration: InputDecoration(labelText: "Stop Loss")),
            SizedBox(height: 20),
            ElevatedButton(onPressed: () => postSignal(context), child: Text("🚀 BROADCAST SIGNAL")),
          ],
        ),
      ),
    );
  }
}

// --- 3. USER DASHBOARD (Tabs: Signals, Risk Calc, Bubbles) ---
class UserDashboard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text("Member Area"),
          bottom: TabBar(
            indicatorColor: Colors.orangeAccent,
            tabs: [Tab(text: "Signals"), Tab(text: "Risk Calc"), Tab(text: "Market")],
          ),
        ),
        body: TabBarView(
          children: [
            SignalListTab(),
            RiskCalcTab(),
            Center(child: Text("Crypto Bubbles - Coming Soon (WebView)")),
          ],
        ),
      ),
    );
  }
}

// --- 4. SIGNAL LIST TAB (Live from Firebase) ---
class SignalListTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      stream: FirebaseFirestore.instance.collection('signals').orderBy('timestamp', descending: true).snapshots(),
      builder: (context, AsyncSnapshot<QuerySnapshot> snapshot) {
        if (!snapshot.hasData) return Center(child: CircularProgressIndicator());
        return ListView(
          padding: EdgeInsets.all(10),
          children: snapshot.data!.docs.map((doc) {
            return Card(
              color: Color(0xFF1A1A1A),
              child: ListTile(
                leading: Icon(Icons.trending_up, color: Colors.greenAccent),
                title: Text("${doc['pair']}", style: TextStyle(fontWeight: FontWeight.bold)),
                subtitle: Text("Entry: ${doc['entry']}\nTP: ${doc['tp']} | SL: ${doc['sl']}"),
                trailing: Text("${doc['status']}", style: TextStyle(color: Colors.orangeAccent)),
                isThreeLine: true,
              ),
            );
          }).toList(),
        );
      },
    );
  }
}

// --- 5. RISK CALCULATOR TAB ---
class RiskCalcTab extends StatefulWidget {
  @override
  _RiskCalcTabState createState() => _RiskCalcTabState();
}

class _RiskCalcTabState extends State<RiskCalcTab> {
  final _balance = TextEditingController();
  final _riskPercent = TextEditingController();
  String result = "Enter values to calculate";

  void calculate() {
    double bal = double.tryParse(_balance.text) ?? 0;
    double risk = double.tryParse(_riskPercent.text) ?? 0;
    double finalRisk = bal * (risk / 100);
    setState(() {
      result = "You should only risk: \$$finalRisk";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.all(20),
      child: Column(
        children: [
          TextField(controller: _balance, decoration: InputDecoration(labelText: "Wallet Balance ($)"), keyboardType: TextInputType.number),
          TextField(controller: _riskPercent, decoration: InputDecoration(labelText: "Risk % (e.g. 2)"), keyboardType: TextInputType.number),
          SizedBox(height: 20),
          ElevatedButton(onPressed: calculate, child: Text("Calculate Risk Amount")),
          SizedBox(height: 30),
          Text(result, style: TextStyle(fontSize: 18, color: Colors.greenAccent)),
        ],
      ),
    );
  }
}
