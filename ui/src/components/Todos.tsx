import { Container, Input, Stack } from "@chakra-ui/react";
import { ChangeEvent, createContext, FormEvent, useContext, useEffect, useState } from "react";


interface Todo {
    id: string;
    item: string;
}

const TodosContext = createContext({
    todos: [], fetchTodos: () => {}
})

function AddTodo() {
    const [item, setItem] = useState("")
    const {todos, fetchTodos} = useContext(TodosContext)

    const handleInput = (event: ChangeEvent<HTMLInputElement>) => {
        setItem(event.target.value)
    }

    const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        const newTodo = {
            "id": todos.length + 1,
            "item": item
        }

        fetch("http://localhost:7777/todo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newTodo)
        }).then(fetchTodos)
    }

    return (
        <form onSubmit={handleSubmit}>
            <Input
                pr="4.5rem"
                type="text"
                placeholder="Add a todo item"
                aria-label="Add a todo item"
                onChange={handleInput}
            />
        </form>
    )
}

export default function Todos() {
    const [todos, setTodos] = useState([])
    const fetchTodos = async () => {
        const response = await fetch("http://localhost:7777/todo")
        const todos = await response.json()
        setTodos(todos.data)
    }
    useEffect(() => {
        fetchTodos()
    }, [])

    return (
        <TodosContext.Provider value={{todos, fetchTodos}}>
            <Container maxW="container.x1" pt="100px">
                <AddTodo />
                <Stack gap={5}>
                    {todos.map((todo: Todo) => (
                        <b key={todo.id}>{todo.item}</b>
                    ))}
                </Stack>
            </Container>
        </TodosContext.Provider>
    )
}
