library(ggplot2)

data <- read.csv("sub_matrix.csv")

data$Substitution.Matrix <- reorder(data$Substitution.Matrix, -data$F.score)

ggplot(data, aes(x = Substitution.Matrix, y = F.score, fill = Substitution.Matrix)) +
  geom_bar(stat = "identity", fill = "skyblue", color = "black", width = 0.7) +
  geom_hline(yintercept = 0.2, linetype = "dashed", color = "darkblue", size = 1) +
  labs(title = "", 
       x = "Substitution Matrix", 
       y = "Mean F-Score") +
  theme_minimal() +
  theme(legend.position = "none", axis.text.x = element_text(angle = 90, hjust = 1.5, vjust = 0.5, size = 10))
