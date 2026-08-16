import "./loading-screen.css";

export default function LoadingScreen({ theme }) {
  return (
    <main className={`loading-screen loading-screen-${theme}`} aria-live="polite" aria-label="A preparar a Edukangola">
      <div className="loading-brand">
        <div className="loading-logo-wrap"><img src="/eduka-mark.png" alt="" /></div>
        <div className="loading-wordmark">eduk<span>angola</span></div>
      </div>
      <div className="loading-progress" aria-hidden="true"><span /></div>
      <p>A preparar o seu próximo passo.</p>
    </main>
  );
}
