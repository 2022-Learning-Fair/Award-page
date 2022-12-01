import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Login from "./Login";
import Main from "./Main";
function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/*" element={<Main />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
