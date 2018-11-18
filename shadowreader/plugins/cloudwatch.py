class MetricEmitter:
    """ Push load test metrics into CloudWatch """
    def __init__(self, metric: dict):
        from libs import cloudwatch as cw

        try:
            self.name = metric["name"]
            self.stage = metric["stage"]
            self.lambda_name = metric["lambda_name"]
            self.app = metric["app"]
            self.identifier = metric["identifier"]
            self.mytime = metric["mytime"]
            self.val = metric["val"]

            if "resolution" in metric:
                self.resolution = metric["resolution"]
            else:
                self.resolution = 60

        except KeyError as e:
            raise ValueError(
                f"MetricEmitter is missing metric details: {type(e)}, {e}, {metric}"
            )
        
        self.resp = cw.put_lambda_metric_w_app_and_env_to_test(
            self.name,
            self.stage,
            self.lambda_name,
            self.app,
            self.identifier,
            mytime=self.mytime,
            val=self.val,
            storage_resolution=self.resolution,
        )

        if "ResponseMetadata" in self.resp:
            self.status_code = self.resp["ResponseMetadata"]["HTTPStatusCode"]
        else:
            raise IOError(f"Error emitting metrics to CloudWatch")

    def __str__(self):
        L = [
            f"name={self.name}",
            f"stage={self.stage}",
            f"app={self.app}",
            f"identifier={self.identifier}",
            f"mytime={self.mytime.dt.isoformat()}",
            f"val={self.val}",
            f"status_code={self.status_code}",
        ]
        s = f'{self.__class__.__qualname__}({", ".join(map(str, L))})'
        return s


def main(metric: dict):
    MetricEmitter(metric)
