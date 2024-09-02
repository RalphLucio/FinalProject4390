import AccentButton from "./components/AccentButton";
import Footer from "./components/Footer";
import SecondaryButton from "./components/SecondaryButton";

export default function Home() {
  const signIn = "Sign In";
  const signUp = "Sign Up";
  return (
    <div className="bg-background-100 w-screen h-screen grid grid-cols-1 gap-4 content-between">
      <div></div>
      <div>
        <div className="flex items-center justify-center ">
          <h1 className=" text-text-950 text-2xl">
            Medi<span className="font-bold text-accent-500">Scan</span>
          </h1>
        </div>
        <div className="flex items-center justify-center">
          <SecondaryButton text={signUp} />
          <AccentButton text={signIn} />
        </div>
      </div>
      <div className="mb-9">
        <Footer />
      </div>
    </div>
  );
}
