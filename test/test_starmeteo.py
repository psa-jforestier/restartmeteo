import subprocess
import sys
import unittest
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
DATETIME = "2020-01-01:12:34:56"


class TimeOptionTests(unittest.TestCase):
    def run_starmeteo(self, *arguments):
        command = [sys.executable, "../starmeteo.py", *arguments]
        print(f"Running: {subprocess.list2cmdline(command)}", flush=True)
        return subprocess.run(
            command,
            cwd=TEST_DIR,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_attached_datetime_aliases_match_separated_argument(self):
        expected = self.run_starmeteo("-time", DATETIME)
        self.assertEqual(expected.returncode, 0, expected.stderr)

        for option in ("--time", "-t", "-time"):
            with self.subTest(option=option):
                actual = self.run_starmeteo(f"{option}:{DATETIME}")
                self.assertEqual(actual.returncode, 0, actual.stderr)
                self.assertEqual(actual.stdout, expected.stdout)

    def test_sample_datetime_encodes_to_expected_frame1(self):
        result = self.run_starmeteo(
            "--time", "2020-08-19:12:46",
            "--area", "2,10,27,28,45,51,60,75,77,78,89,91,92,93,94,95",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "lN:&5s  9 $*-G%K-Y+FSK-NY=O7Q?,\n")

    def test_sample_datetime_encodes_to_expected_frame2(self):
        result = self.run_starmeteo(
            "--time", "2020-09-20:22:46",
            "--area", "2,10,27,28,45,51,60,75,77,78,89,91,92,93,94,95",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'o$:8%"  9 $*-G%K-Y+FSK-NY=O7Q?,\n')
    def test_sample_datetime_encodes_to_expected_frame3(self):
        T = [
            "2026-01-01:12:34:56", "75",    'lM006I  8&6%)0',
            "2020-06-15:08:00:00", "75",    'n !E5"  8&6%)0',
            "2021-12-31:20:30:00", "75",    'nCs,55  8&6%)0',
            "2021-06-15:20:00:00", "75,95", 'np!E55  8*7?4m'
        ]
        for i in range(len(T) // 3):
            date_time, area, expected_frame = T[i*3:(i+1)*3]
            result = self.run_starmeteo(
                "--time", date_time,
                "--area", area,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, f'{expected_frame}\n')

    def test_forecast1(self):
        F = [
            "75", "0,0,0,0,0,0,0",          '1+!.0$       /',
            "92", "0,0,0,0,0,0,0",          '1<! 0$       /',
            "10", "0,0,0,0,0,0,0",          '0*!)0$       /',
            "75", "-10,10,0x12,0x12,0x12,0x12,0x12", '1+!.,% 2$A(2$N',
            "75", ["21,13,0x0d,0x19,0x02,0x43,0x1d",
                   "13,10,0x07,0x43,0x43,0x07,0x43",
                   "16,9,0x43,0x99,0x43,0x02,0x19",
                   "19,11,0x48,0x05,0x48,0x48,0x5b"], "1+!.85,-&0)s'44U '0T,'0W5DEsF4,\"&;65%(!4A(6T"
        ]
        for i in range(len(F) // 3):
            area, forecast, expected_frame = F[i*3:(i+1)*3]
            if isinstance(forecast, list):                
                args = ["--area", area]
                for f in forecast:
                    args.extend(["--forecast", f])
                result = self.run_starmeteo(*args)
            else:
                result = self.run_starmeteo(
                    "--area", area,
                    "--forecast", forecast,
                )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, f'{expected_frame}\n')

    def test_extended_forecast1(self):
            F = [
                "89", ["12,0,0x47,0x18,0x47,0x02,0x1a,90",
                       "13,1,0x43,0x99,0x02,0x02,0x99,40",
                       "14,7,0x07,0x6e,0x07,0x07,0x1a,95",
                       "19,8,0x48,0x5b,0x48,0x48,0x5b,50",
                       "18,10,0x05,0x05,0x05,0x05,0x5b,90",
                       "21,11,0x48,0x5b,0x48,0x48,0x5b,80"], '!9!)4D!\'&$<"&N4T%sF0("F35$<\';p<\'&O64A(6TA(6U6% %!04%6m85%(6TA(6XS,S&9F;=W==W=lS,RkNk. L'
            ]
            for i in range(len(F) // 3):
                area, forecast, expected_frame = F[i*3:(i+1)*3]
                if isinstance(forecast, list):                
                    args = ["--area", area]
                    for f in forecast:
                        args.extend(["--forecast", f])
                    result = self.run_starmeteo(*args)
                else:
                    result = self.run_starmeteo(
                        "--area", area,
                        "--forecast", forecast,
                    )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, f'{expected_frame}\n')
if __name__ == "__main__":
    unittest.main()