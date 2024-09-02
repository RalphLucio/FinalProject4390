export default function SecondaryButton(props){
  return(
    <>
      <button type="button" className="text-text-950 bg-secondary-700 hover:bg-secondary-800 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 ">{props.text}</button>
    </>
  )
}