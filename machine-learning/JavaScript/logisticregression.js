class LogisticRegression {
  constructor (inputs) {
      this.inputs = inputs;
      var weights = [];
      for (var i = 0; i < inputs; i++){
         weights.push (Math.random());
      }
      this.weights = weights;
  }

}
