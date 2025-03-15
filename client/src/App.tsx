import { FlickeringGrid } from "./components/magicui/flickering-grid";

const App = () => {
  return (
    <div className="flex-auto">
      <FlickeringGrid
        className="absolute inset-0 -z-1 size-full bg-primary"
        squareSize={4}
        gridGap={6}
        color="#6B7280"
        maxOpacity={0.5}
        flickerChance={0.1}
      />
    </div>
  );
};

export default App;
