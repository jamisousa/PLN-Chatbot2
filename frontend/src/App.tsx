import React, { useEffect, useState } from "react";
import "./App.css";
import thinkingimg from "../src/assets/thinking.png";
import happyimg from "../src/assets/happy.png";
import angryimg from "../src/assets/angry.png";
import neutralimg from "../src/assets/neutral.png";
import styles from "./Styles.module.css";

function App() {
  const [loading, setLoading] = useState(false);
  const [emotion, setEmotion] = useState("none");
  const [result, setResult] = useState("");
  const [reply, setReply] = useState("");

  const handleSendUserInput = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    const userInput = document.getElementById(
      "userinput"
    ) as HTMLInputElement | null;
    const sentence = userInput ? userInput.value : "";

    try {
      const response = await fetch("http://127.0.0.1:5000/avaliar_sentimento", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sentence }),
      });

      if (response.ok) {
        const data = await response.json();
        const sentiment = data.sentimento;

        if (sentiment === "frase neutra") {
          setEmotion("neutral");
        } else if (sentiment === "frase positiva") {
          setEmotion("happy");
        } else if (sentiment === "frase negativa") {
          setEmotion("angry");
        }
        console.log(emotion);
        setTimeout(() => {
          setLoading(false);
        }, 1000);
      } else {
        console.error("Erro na chamada à API");
        setLoading(false);
      }
    } catch (error) {
      console.error("Erro ao processar a resposta da API", error);
      setLoading(false);
    }
  };

  const generateReply = (emotion: string) => {
    if (emotion == "happy") {
      setReply(
        "Thanks for your feedback! I'll send your compliment to our support team. Have a nice day! 💙"
      );
    } else if (emotion == "angry") {
      setReply(
        "No need to be so rude! I'm sorry we couldn't meet your expectations. Your response was submitted and our support team will be working on it. Thank you."
      );
    } else {
      setReply(
        "I don't think I understand what you said, but I'll send your review to the human team, I'm sure they'll understand it better! ✨"
      );
    }
  };

  let imgStyle = loading
    ? `${styles.charImg} ${styles.shake}`
    : `${styles.charImg}`;

  useEffect(() => {
    generateReply(emotion);
  }, [emotion]);

  return (
    <div className={styles.fullcontent}>
      <div className={styles.botcontainer}>
        {!loading ? (
          <>
            {emotion == "happy" ? (
              <>
                {" "}
                <img src={happyimg} className={imgStyle} />
              </>
            ) : emotion == "angry" ? (
              <>
                {" "}
                <img src={angryimg} className={imgStyle} />
              </>
            ) : (
              <>
                {" "}
                <img src={neutralimg} className={imgStyle} />
              </>
            )}
          </>
        ) : (
          <>
            {" "}
            <img src={thinkingimg} className={imgStyle} />
          </>
        )}
        {reply && emotion != "none" ? (
          <div className={styles.introText}>
            <h1>{reply && !loading ? reply : "Im thinking..."}</h1>
          </div>
        ) : (
          <>
            <div className={styles.introText}>
              <h1>Hi there! I'm Leo 👋</h1>
              <h1>
                Tell me your feedback and I'll register it for our team
                analysis!
              </h1>
            </div>
          </>
        )}
      </div>

      <form>
        <h3>My review is...</h3>
        <div className={styles.userinputentry}>
          <input type="text" id="userinput" className={styles.userinput} />
          <button onClick={handleSendUserInput}>{">"}</button>
        </div>
      </form>
    </div>
  );
}

export default App;
