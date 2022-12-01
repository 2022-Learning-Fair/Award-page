import React from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useEffect } from "react";
import "../css/main.css";
function Main() {
  const sessionCheckJson = {
    token: sessionStorage.getItem("login-token"),
    name: sessionStorage.getItem("login-name")
  };
  const navigate = useNavigate();
  async function session_check_api(sessionChkreqJson) {
    try {
      const response = await axios.post(
        "/api/session-check",
        JSON.stringify(sessionChkreqJson),
        {
          headers: {
            "Content-Type": `application/json`
          }
        }
      );

      if (response["data"]["session"] === "deactive") {
        navigate("/");
      }
    } catch (e) {
      console.log(e);
    }
  }
  useEffect(() => {
    session_check_api(sessionCheckJson);
  }, []);

  //-----------세션 체크 완료------------------

  return (
    <div>
      <center>
        <img
          class="awards"
          src={`${process.env.PUBLIC_URL}/awards.png`}
          alt="awards.png"
        />
      </center>
    </div>
  );
}

export default Main;
