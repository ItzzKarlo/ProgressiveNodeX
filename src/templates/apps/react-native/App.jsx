import React from "react";
import { SafeAreaView, StyleSheet, Text } from "react-native";

export default function App() {
  return (
    <SafeAreaView style={styles.page}>
      <Text style={styles.kicker}>ProgressiveNodeX</Text>
      <Text style={styles.title}>React Native starter</Text>
      <Text style={styles.body}>Edit App.jsx to build your mobile app.</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    backgroundColor: "#0f172a"
  },
  kicker: {
    color: "#38bdf8",
    fontWeight: "700",
    marginBottom: 12
  },
  title: {
    color: "white",
    fontSize: 36,
    fontWeight: "800",
    textAlign: "center"
  },
  body: {
    color: "#cbd5e1",
    marginTop: 12,
    textAlign: "center"
  }
});