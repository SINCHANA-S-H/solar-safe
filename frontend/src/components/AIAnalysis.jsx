function AIAnalysis() {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 mt-8">

      <h2 className="text-2xl font-bold mb-6">
        AI Analysis
      </h2>

      <div className="space-y-4">

        <p>
          <strong>Fault Type:</strong> Hotspot
        </p>

        <p>
          <strong>Severity:</strong> High
        </p>

        <p>
          <strong>Confidence:</strong> 98.4%
        </p>

        <p>
          <strong>Affected Cell:</strong> Cell 34
        </p>

        <p>
          <strong>Temperature:</strong> 86°C
        </p>

        <p>
          <strong>Estimated Power Loss:</strong> 13%
        </p>

        <p className="text-red-600 font-semibold">
          Recommendation:
          Replace damaged cell immediately.
        </p>

      </div>

    </div>
  );
}

export default AIAnalysis;