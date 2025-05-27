#install.packages("tidyverse")  #if needed
library(tidyverse)
library(patchwork)

data <- read.csv("bali3_benchmark.csv")

data_long <- data %>%
  pivot_longer(cols = c(MUSCLE_F, MergeAlign_F), 
               names_to = "algorithm", 
               values_to = "f_score")

data_long$algorithm <- factor(data_long$algorithm, levels = c("MUSCLE_F", "MergeAlign_F"))

#boxplot
box <- ggplot(data_long, aes(x = algorithm, y = f_score, fill = algorithm)) +
  geom_boxplot() +
  labs(title = "B",
       x = "MSA Algorithm",
       y = "F-Score") +
  scale_x_discrete(labels = c("MUSCLE_F" = "MUSCLE", "MergeAlign_F" = "MergeAlign")) +
  theme_minimal() +
  theme(legend.position = "none")

# Paired Scatter Plot
scatter <- ggplot(data, aes(x = MUSCLE_F, y = MergeAlign_F)) +
  geom_point(aes(color = File), size = 3, alpha = 0.7) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "red") +
  labs(title = "A",
       x = "MUSCLE F-score", 
       y = "MergeAlign F-score") +
  theme_minimal() +
  theme(legend.position = "none")

scatter + box

# Wilcoxon test
data$diff <- data$MergeAlign_F - data$MUSCLE_F

ggplot(data, aes(x = diff)) + 
  geom_histogram(bins = 10, fill = "skyblue", color = "black")

shapiro.test(data$diff)

wilcox_test_result <- wilcox.test(data$MergeAlign_F, data$MUSCLE_F, paired = TRUE)

print(wilcox_test_result)
